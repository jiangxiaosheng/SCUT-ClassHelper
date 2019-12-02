# -*- coding: utf-8 -*-
from flask import url_for, render_template, redirect, request, current_app, session, Response
from .. import db
from app.models import Teacher, User, Course, StudentCourse, Announcement
from . import course
from flask_login import login_required, current_user
from .forms import JoinCourseForm
from config import basedir, resources_base_dir
from ..utils import *
import re

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
@course.route('/join-course', methods=['GET', 'POST'])
@login_required
def join_course():
    form = JoinCourseForm()
    if form.validate_on_submit():
        session['course_id_or_name'] = form.id_or_name.data #存到session里
        return redirect(url_for('.courses')) #重定向到courses路由，交给courses函数处理
    return render_template('course/join_course.html', form=form)


#显示查询出的所有课程
@course.route('/courses', methods=['POST', 'GET'])
@login_required
def courses():
    id_or_name = session['course_id_or_name']
    if re.match(r'^\d\d*\d$', id_or_name):
        courses = Course.query.filter_by(course_id=id_or_name).all()
    else:
        courses = Course.query.filter_by(name=id_or_name).all()
    return render_template('course/courses.html', courses=courses)


#TODO:删除课程路由，删除完之后重定位到index，相当于刷新了页面
@course.route('/drop-course', methods=['POST', 'GET'])
@login_required
def drop_course():
    if current_user.role.name is not None:
        if current_user.role.name == 'Student':
            course_id = request.values.get('course_id')
            record = StudentCourse.query.filter_by(course_id=course_id, student_id=current_user.student.student_id).first()
            db.session.delete(record)
            db.session.commit()
        #TODO
        else:
            course_id = request.values.get('course_id')
            record = Course.query.filter_by(course_id=course_id).first()
            db.session.delete(record)
            db.session.commit()
        return redirect(url_for('.index'))
    else:
        return render_template('500.html')


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


#TODO:在线考试
@course.route('/tests')
@login_required
def tests():
    pass


#TODO:聊天室
@course.route('/chatroom/<int:course_id>')
@login_required
def chatroom(course_id):
    courses = StudentCourse.query.filter_by(student_id=current_user.student.student_id).all()
    course = Course.query.filter_by(course_id=course_id).first()
    return render_template('course/chatroom.html', courses=[c.course for c in courses], course=course)


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

