from flask import url_for, render_template, redirect
from . import course
from flask_login import login_required, current_user

#TODO:显示所有课程，学生显示选课，老师显示开设的课
@course.route('/')
@login_required
def index():
    if current_user.role.name == 'Student':
        courses = current_user.student.courses #学生加入的课程
        return render_template('course/index.html', courses=[c.course for c in courses])
    elif current_user.role.name == 'Teacher':
        courses = current_user.teacher.courses #老师创建的课程
        return render_template('course/index.html', courses=[c.course for c in courses])


#TODO：加入课程
@course.route('/join-course')
@login_required
def join_course():

    return render_template('course/join_course.html')


#TODO：课程资源
@course.route('/resources')
@login_required
def resources():
    pass


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


