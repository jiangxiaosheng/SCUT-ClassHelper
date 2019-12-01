# -*- coding: utf-8 -*-
from flask import url_for, render_template, redirect, request, current_app, session, send_from_directory
from .. import db
from app.models import Teacher, User, Course, StudentCourse
from . import course
from flask_login import login_required, current_user
from .forms import JoinCourseForm

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


@course.route('/join-course', methods=['GET', 'POST'])
@login_required
def join_course():
    form = JoinCourseForm()
    if form.validate_on_submit():
        session['course_id'] = form.id.data #存到session里
        return redirect(url_for('.courses')) #重定向到courses路由，交给courses函数处理
    return render_template('course/join_course.html', form=form)


@course.route('/courses', methods=['POST', 'GET'])
@login_required
def courses():
    courses = Course.query.filter_by(course_id=session['course_id']).all()
    print(courses)
    return render_template('course/courses.html', courses=courses)


#TODO:删除课程路由，删除完之后重定位到index，相当于刷新了页面
@course.route('/drop-course', methods=['POST', 'GET'])
@login_required
def drop_course():
    if current_user.role.name is not None:
        if current_user.role.name == 'Student':
            course_id = request.values.get('course_id')
            record = StudentCourse.query.filter_by(course_id=course_id, student_id=current_user.student.student_id).first()
            print(record)
            db.session.delete(record)
            db.session.commit()
        #TODO
        else:
            course_id = request.values.get('course_id')
            record = Course.query.filter_by(course_id=course_id).first()
            print(record)
            db.session.delete(record)
            db.session.commit()
        return redirect(url_for('.index'))
    else:
        return render_template('500.html')


#TODO：课程资源
@course.route('/resources')
@login_required
def resources(id):
    if request.method == 'GET':
        pass


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


