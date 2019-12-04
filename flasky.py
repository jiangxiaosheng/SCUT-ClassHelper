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

#客户端发送消息,room和课程id一样
@socketio.on('send_message')
def send_message(msg):
    course_id = msg['course_id']
    room = course_id
    user = User.query.filter_by(id=msg['user_id']).first()
    try:
        insert_message(course_id, msg)
        emit('update_message', {
            'flag': 'success', #标志位，表明是否发送成功，一般都是成功的
            'nickname': user.nickname,
            'user_id': user.id,
            'headicon_url': user.headicon_url,
            'content': msg['content'],
            'timestamp': str(localtime()),
        }, room=room)
    except:
        emit('update_message', {'data': 'failed'})


#有新的客户端连接进来
@socketio.on('connected')
def connected(msg):
    room = msg['room']
    join_room(room)
    user = User.query.filter_by(id=msg['user_id']).first()
    emit('accept_connection', {
        'nickname': user.nickname
    }, room=room)
    open('YES.txt', 'w').write(','.join(rooms()))


@socketio.on('disconnected')
def disconnected(msg):
    room = msg['room']
    leave_room(room)
    user = User.query.filter_by(id=msg['user_id']).first()
    emit('accept_disconnection', {
        'nickname': user.nickname
    }, room=room)
    open('YES.txt', 'w').write(','.join(rooms()))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, Permission=Permission, User=User, Student=Student, Teacher=Teacher,
                StudentCourse=StudentCourse, Course=Course, Post=Post, Comment=Comment, Announcement=Announcement,
                PostLike=PostLike)

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, debug=True)
