from flask import url_for, render_template, redirect
from . import course
from flask_login import login_required, current_user

@course.route('/')
@login_required
def index():
    courses = current_user.student.courses

    return render_template('course/index.html', courses=[c.course for c in courses])


@course.route('/join-course')
def join_course():
    return render_template('course/join_course.html')


