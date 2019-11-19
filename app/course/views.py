from flask import url_for, render_template
from . import course

@course.route('/')
def index():

    return render_template('course/index.html')


@course.route('/join-course')
def join_course():
    return render_template('course/course.html')


