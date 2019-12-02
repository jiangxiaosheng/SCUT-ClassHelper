# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import *
from flask_migrate import Migrate
import os
from flask_socketio import *
from app.utils import *


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

async_mode = None
socketio = SocketIO(app=app, async_mode=async_mode)

'''
在服务器上换成这个
async_mode = 'gevent'
socketio = SocketIO(app=app, async_mode=async_mode)
'''

#客户端发送消息
@socketio.on('send_message')
def send_message(msg):
    try:
        course_id = msg['course_id']
        insert_message(course_id, msg)
        emit('update_message', {'data': 'success'})
    except:
        emit('update_message', {'data': 'failed'})


#有新的客户端连接进来
@socketio.on('connected')
def connected(msg):
    emit('accept_connection', {
        'user_id': msg['user_id']
    }, broadcast=True)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, Permission=Permission, User=User, Student=Student, Teacher=Teacher,
                StudentCourse=StudentCourse, Course=Course, Post=Post, Comment=Comment, Announcement=Announcement,
                PostLike=PostLike)

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, debug=True)
