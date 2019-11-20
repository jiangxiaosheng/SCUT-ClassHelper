from flask import url_for, render_template
from . import course
from flask_login import login_required

@course.route('/')
@login_required
def index():

    return render_template('course/index.html')


@course.route('/join-course')
def join_course():
    return render_template('course/course.html')


