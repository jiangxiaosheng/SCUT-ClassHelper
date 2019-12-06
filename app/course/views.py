# -*- coding: utf-8 -*-
import json

from flask import url_for, render_template, redirect, request, current_app, session, Response
from .. import db
from app.models import Teacher, User, Course, StudentCourse, Announcement, Test, Answer, CheckTest, Student
from . import course
from flask_login import login_required, current_user
from .forms import *
from config import basedir, resources_base_dir
from ..utils import *
import re
from ..decorators import *

#TODO:显示所有课程，学生显示选课，老师显示开设的课
@course.route('/')
@login_required
def index():
    if current_user.role is not None and current_user.role.name == 'Student':
        page = request.args.get('page', 1, type=int)
        pagination = current_user.student.courses.paginate(
            page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False)
        courses = [item.course for item in pagination.items]
        return render_template('course/index.html', courses=courses, pagination=pagination)
    elif current_user.role.name == 'Teacher':
        page = request.args.get('page', 1, type=int)
        pagination = current_user.teacher.courses.paginate(
            page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False) #老师创建的课程
        courses = [item for item in pagination.items]
        return render_template('course/index.html', courses=courses, pagination=pagination)


#TODO:加入课程
@course.route('/query-course', methods=['GET', 'POST'])
@login_required
def query_course():
    form = JoinCourseForm()
    if form.validate_on_submit():
        session['course_id_or_name'] = form.id_or_name.data #存到session里
        return redirect(url_for('.courses')) #重定向到courses路由，交给courses函数处理
    return render_template('course/query_course.html', form=form)


@course.route('/join-course/<int:course_id>')
@login_required
@permission_required(Permission.JOINCOURSE)
def join_course(course_id):
    record = StudentCourse(
        student_id=current_user.student.student_id,
        course_id=course_id
    )
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('.index'))



#显示查询出的所有课程
@course.route('/courses', methods=['POST', 'GET'])
@login_required
def courses():
    id_or_name = session['course_id_or_name']
    if re.match(r'^[0-9]*$', id_or_name):
        courses = Course.query.filter_by(course_id=id_or_name).all()
    else:
        courses = Course.query.filter_by(name=id_or_name).all()
    return render_template('course/courses.html', courses=courses)


#TODO:删除课程路由，删除完之后重定位到index，相当于刷新了页面
@course.route('/drop-course', methods=['POST', 'GET'])
@login_required
def drop_course():
    if current_user.role.name is not None:
        if current_user.role.name == 'Student': #如果是学生就退出班级，在StudentCourse表中删掉一条记录
            course_id = request.values.get('course_id')
            record = StudentCourse.query.filter_by(course_id=course_id, student_id=current_user.student.student_id).first()
            db.session.delete(record)
            db.session.commit()
        #TODO
        else: #如果是老师或者管理员，就直接解散，删掉Course表中的一条记录
            course_id = request.values.get('course_id')
            record = Course.query.filter_by(course_id=course_id).first()
            db.session.delete(record)
            db.session.commit()
            drop_messsage_table(course_id) #解散的时候要在mysql中删表
        return redirect(url_for('.index'))
    else:
        return render_template('500.html')


#老师创建课程视图
@course.route('/create-course', methods=['GET', 'POST'])
@permission_required(Permission.CREATECOURSE)
def create_course():
    form = CreateCourseForm()
    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            teacher_id=current_user.teacher.teacher_id,
            about_course=form.about_course.data,
            college=form.college.data,
            since=localtime()
        )
        db.session.add(course)
        db.session.commit()
        c = Course.query.offset(Course.query.count() - 1).first() #这里要从数据库中拿，因为course_id只有插入到数据库中才能确定
        create_message_table(c.course_id) #创建课程的时候要在mysql中建表
        create_resource_dir(c.course_id) #创建资源目录

        return redirect(url_for('course.index'))
    return render_template('course/create_course.html', form=form)



#TODO：课程资源,还没有实现分页功能
@course.route('/resources/<int:course_id>', methods=['GET'])
@login_required
def resources(course_id):
    dir = os.path.join(resources_base_dir, str(course_id))
    #文件列表，每一项是个元组，（文件名，文件绝对路径，文件后缀名（.jpg ...）,文件上传时间）
    file_list = zip(os.listdir(dir), [os.path.join(dir, filename) for filename in os.listdir(dir)],
                    [file_extension(filename) for filename in os.listdir(dir)],
                    [fileTime(os.path.join(dir, filename))[1] for filename in os.listdir(dir)])
    return render_template('course/resources.html', resources=file_list, course_id=course_id)


#下载资源
@course.route('/resources/<int:course_id>/download', methods=['GET'])
def download_resources(course_id):
    filename = request.args.get('filename') #拿到资源文件名
    dir = os.path.join(resources_base_dir, str(course_id)) #拿到对应课程的目录

    # 先判断要找的资源在不在服务器中，如果不在就404，这样也可以防止注入攻击
    if filename not in os.listdir(dir):
        return render_template('404.html', message='您要找的资源不存在')

    def send_file():
        store_path = os.path.join(dir, filename)
        with open(store_path, 'rb') as targetfile:
            while 1:
                data = targetfile.read(20 * 1024 * 1024)  # 每次读取20M
                if not data:
                    break
                yield data

    response = Response(send_file(), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename=%s' % filename  # 这行代码是为了下载时显示文件名
    return response


#TODO:显示出该课程所有考试信息
@course.route('/tests/<int:course_id>')
@login_required
def tests(course_id):
    all_tests = Test.query.filter_by(course_id=str(course_id)).all()
    allow = []
    if current_user.role.name == 'Student':
        for test in all_tests:
            record = CheckTest.query.filter_by(
                student_id=current_user.student.student_id,
                test_id=test.id
            ).first()
            if record is None:
                allow.append(True)
            else:
                if record.allow == True:
                    allow.append(True)
                else:
                    allow.append(False)
    else:
        allow = [True] * len(all_tests)
    return render_template('course/tests.html', all_tests=all_tests, course_id=course_id, allow=allow)


#TODO:发布考试
@course.route('/create-test/<int:course_id>', methods=['GET', 'POST'])
@permission_required(Permission.CREATETEST)
def create_test(course_id):
    return render_template('course/create_test.html', course_id=course_id)


#参加考试
@course.route('/join-test/<int:course_id>')
def join_test(course_id):
    test_name = request.values.get("test_name")
    test = Test.query.filter_by(course_id=course_id, name=test_name).first()
    content = json.loads(test.content)
    metadata = {
        "name": content['name'],
        "count": len(content['questions']),
        "course_id": course_id,
        "test_id": test.id,
    }
    question_count = len(content['questions'])
    questions = []
    for i in range(question_count):
        q = content['questions'][i]
        if q['type'] == 'simple':
            questions.append((q['id'], q['type'], q['content']['title']))
        else:
            questions.append((q['id'], q['type'], q['content']['title'], q['content']['A'], q['content']['B'], q['content']['C'], q['content']['D']))
    #open('test.txt', 'w').write(str(questions))
    return render_template('course/join_test.html', questions=questions, metadata=metadata)


#老师查看学生答题情况
@course.route('/show-all-answers/<int:course_id>')
@permission_required(Permission.CHECKANSWERS)
def show_all_answers(course_id):
    test_id = request.values.get("test_id")
    records = StudentCourse.query.filter_by(course_id=course_id).all()
    students = [i.student for i in records] #该门课的所有学生
    has_commit = []
    url = []
    for s in students:
        if Answer.query.filter_by(student_id=s.student_id, test_id=test_id).first(): #如果考过了
            url.append(url_for('course.show_answer', student_id=s.student_id, test_id=test_id))
        else:
            url.append('')
    return render_template('course/show_student_answers.html', students=students, test_id=test_id,
                           has_commit=has_commit, url=url)


#TODO:需要将学生的答案渲染出来
@course.route('/show-answer')
@permission_required(Permission.CHECKANSWERS)
def show_answer():
    student_id = request.values.get("student_id")
    test_id = request.values.get("test_id")
    answer = Answer.query.filter_by(
        student_id=student_id,
        test_id=test_id
    ).first().answer
    test = Test.query.filter_by(
        test_id=test_id
    ).first().content
    answer = json.loads(answer)
    test = json.loads(test)
    content = []
    for i in range(len(test['questions'])):
        content.append((i + 1, test['questions'][i]['content']['title'], answer['content'][i]['answer']))
    return render_template('course/answer.html', content=content)



#TODO:聊天室
#TODO：目前还不能防止用户进入自己课程之外的聊天室
@course.route('/chatroom/<int:course_id>')
@login_required
def chatroom(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    res = get_chat_history(course_id)
    chat_history = []
    for c in res:
        user = User.query.filter_by(id=c[0]).first()
        #昵称，头像，消息内容，时间戳
        chat_history.append((user.id, user.nickname, user.headicon_url, c[1], c[2]))
    if current_user.role.name == 'Student':
        courses = StudentCourse.query.filter_by(student_id=current_user.student.student_id).all()
        return render_template('course/chatroom.html', courses=[c.course for c in courses], course=course, chat_history=chat_history)
    elif current_user.role.name == 'Teacher':
        courses = current_user.teacher.courses
        return render_template('course/chatroom.html', courses=courses, course=course, chat_history=chat_history)
    else:
        courses = Course.query.all()
        return render_template('course/chatroom.html', courses=courses, course=course, chat_history=chat_history)


#公告
@course.route('/announcement/<int:course_id>')
@login_required
def announcement(course_id):
    page = request.args.get('page', 1, type=int)
    pagination = Announcement.query.filter_by(course_id=course_id).order_by(Announcement.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False)
    announcements = [item for item in pagination.items]
    return render_template('course/announcement.html', announcements=announcements, pagination=pagination,
                           course_id=course_id)

#老师发布公告
@course.route('/publish-announcement/<int:course_id>', methods=['GET', 'POST'])
@login_required
def publish_announcement(course_id):
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            course_id=course_id,
            timestamp=localtime(),
            title=form.title.data,
            body=form.content.data,
        )
        db.session.add(announcement)
        db.session.commit()
        return redirect(url_for('course.announcement', course_id=course_id))
    return render_template('course/publish_announcement.html', form=form)


@course.route('/publish-resource/<int:course_id>', methods=['GET', 'POST'])
@login_required
def publish_resource(course_id):
    form = PublishResourceForm()
    if form.validate_on_submit():
        file = form.file.data
        file.filename = form.name.data
        path = os.path.join(resources_base_dir, str(course_id), file.filename)
        file.save(path)
        return redirect(url_for('course.resources', course_id=course_id))
    return render_template('course/publish_resource.html', form=form)


#查看历史记录
@course.route('/chat-history/<int:course_id>')
@login_required
def show_chat_history(course_id):
    res = get_chat_history(course_id, all=True)
    chat_history = []
    for c in res:
        user = User.query.filter_by(id=c[0]).first()
        #昵称，头像，消息内容，时间戳
        chat_history.append((user.id, user.nickname, user.headicon_url, c[1], c[2]))
    course = Course.query.filter_by(course_id=course_id).first()
    return render_template('course/chat_history.html', chat_history=chat_history, course=course)

