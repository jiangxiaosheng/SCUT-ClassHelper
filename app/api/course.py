from flask import request, jsonify, redirect, url_for
from .. import db
from . import api
from ..models import Course, StudentCourse, Test
from flask_login import login_required
import json
from ..utils import localtime

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
#TODO:时间还没设置
@api.route('/create-test', methods=['GET', 'POST'])
@login_required
def create_test():
    course_id = request.values.get('course_id')
    content_json = request.values.get('content_json')
    #open('test.txt', 'w').write(content_json)

    content = json.loads(content_json)
    name = content['name']
    #start = content['start']
    start = localtime()
    test = Test(
        name=name,
        course_id=course_id,
        start=start,
        duration=3600,
        content = content_json,
    )
    db.session.add(test)
    db.session.commit()
    return jsonify({
        "flag": True
    })




