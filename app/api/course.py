from flask import request, jsonify, redirect, url_for
from .. import db
from . import api
from ..models import Course, StudentCourse
from flask_login import login_required

@api.route('/drop-course', methods=['POST', 'GET'])
@login_required
def drop_course():
    course_id = request.values.get('course_id')
    print(course_id)
    print(111)
    ptr = {"f": "d"}
    return jsonify(ptr)

