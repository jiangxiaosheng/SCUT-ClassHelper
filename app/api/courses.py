from flask import request, jsonify
from .. import db
from . import api

@api.route('/drop-course', methods=['POST'])
def drop_course():
    course_id = request.values.get('course_id')
