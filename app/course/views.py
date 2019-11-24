# -*- coding: utf-8 -*-
from flask import url_for, render_template, redirect, request, current_app, session
import math
from app.models import Teacher, User, Course
from . import course
from flask_login import login_required, current_user
from .forms import JoinCourseForm

#TODO:显示所有课程，学生显示选课，老师显示开设的课
@course.route('/')
@login_required
def index():
    if current_user.role.name == 'Student':
        page = request.args.get('page', 1, type=int)
        pagination = current_user.student.courses.paginate(
            page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False)
        courses = [item.course for item in pagination.items]
        print(courses)
        return render_template('course/index.html', courses=courses, pagination=pagination)
    elif current_user.role.name == 'Teacher':
        courses = current_user.teacher.courses #老师创建的课程
        return render_template('course/index.html', courses=[c.course for c in courses])


#TODO：加入课程
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
    return render_template('course/courses.html', courses=courses)


def drop_course():
    print('drop')


#TODO：课程资源
@course.route('/resources/<int:id>')
@login_required
def resources(id):
    return url_for('static/course_resources/email.py')


#TODO:在线考试
@course.route('/tests')
@login_required
def tests():
    pass


#TODO:聊天室
@course.route('/chatroom')
@login_required
def chatroom():
    pass


