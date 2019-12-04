from flask import request, jsonify, redirect, url_for
from .. import db
from . import api
from ..models import Course, StudentCourse, Test
from flask_login import login_required
import json

@api.route('/drop-course', methods=['POST', 'GET'])
@login_required
def drop_course():
    course_id = request.values.get('course_id')
    print(course_id)
    print(111)
    ptr = {"f": "d"}
    return jsonify(ptr)


#聊天记录
@api.route('/chat-history', methods=['GET', 'POST'])
@login_required
def chat_history():
    course_id = request.values.get('course_id')


#创建考试
@api.route('/create-test', methods=['GET', 'POST'])
@login_required
def create_test():
    course_id = request.values.get('course_id')
    content_json = request.values.get('content_json')
    content = json.loads(content_json)
    name = content['name']
    test = Test(
        name=name,
        course_id=course_id,
        start=,
        end=,

    )



