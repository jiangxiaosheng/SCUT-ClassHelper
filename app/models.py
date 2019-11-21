import hashlib
from datetime import datetime

import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin
from itsdangerous import Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager

#学生-课程关联表
#TODO:还没有实现多对多关系
class StudentCourse(db.Model):
    __tablename__ = 'studentcourses'
    student_id = db.Column(db.String, db.ForeignKey('students.student_id'), primary_key=True)
    course_id = db.Column(db.String, db.ForeignKey('courses.course_id'), primary_key=True)


#课程表
class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.String, primary_key=True) #课程id
    name = db.Column(db.String) #课程名
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id')) #该课程对应的老师
    since = db.Column(db.DateTime, default=datetime.utcnow) #开课时间
    about_course = db.Column(db.Text) #课程介绍
    college = db.Column(db.String) #课程所属学院
    students = db.relationship('StudentCourse',
                               foreign_keys=[StudentCourse.course_id],
                               backref=db.backref('course', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )

    def __repr__(self):
        return '<Course %r,%r>' % (self.course_id, self.name)


#学生表
class Student(db.Model):
    __tablename__ = 'students'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #用户id
    student_id = db.Column(db.String, unique=True, index=True) #学号
    college = db.Column(db.String) #学生所在学院
    major = db.Column(db.String) #学生专业
    grade = db.Column(db.String) #学生年级
    courses = db.relationship('StudentCourse',
                               foreign_keys=[StudentCourse.student_id],
                               backref=db.backref('student', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return '<Student %r,%r>' % (self.student_id, self.user.name)


#老师表
class Teacher(db.Model):
    __tablename__ = 'teachers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #用户id
    teacher_id = db.Column(db.String, unique=True, index=True) #教师编号
    college = db.Column(db.String) #老师所在学院
    position = db.Column(db.String) #老师职务
    courses = db.relationship('Course', backref='teacher', lazy='dynamic') #通过Course的teacher字段拿到teacher信息

    def __repr__(self):
        return '<Teacher %r,%r>' % (self.teacher_id, self.user.name)

class Permission:
    FOLLOW = 1  # 关注
    COMMENT = 2  # 评论
    WRITE = 4  # 发布
    JOINCLASS = 8   #加入课程
    CREATECLASS = 16    #创建课程
    MODERATE = 32  # 修改
    ADMIN = 64  # 管理员

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True) #默认角色
    permissions = db.Column(db.Integer) #权限
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    #添加权限
    def add_permission(self, per):
        if not self.has_permission(per):
            self.permissions += per

    #移除权限
    def remove_permission(self, per):
        if self.has_permission(per):
            self.permissions -= per

    #重设权限，即删除所有权限
    def reset_permissions(self):
        self.permissions = 0

    #是否拥有某项权限
    def has_permission(self, per):
        return self.permissions & per == per

    #在Role数据库中插入role
    @staticmethod
    def insert_roles():
        roles = {
            'Student': [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT, Permission.JOINCLASS],
            'Teacher': [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT, Permission.CREATECLASS],
            'Administrator': [Permission.COMMENT, Permission.FOLLOW, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'Student' #默认角色是学生
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


#评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text) #评论的原内容
    body_html = db.Column(db.Text) #经过富文本处理的评论内容，保存为HTML格式
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #发表评论的时间戳
    disabled = db.Column(db.Boolean) #该评论是否被管理员禁止的标志位
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) #发表该评论的作者id
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id')) #该评论的动态id

    #每次评论内容发生变化时，该方法被调用，将新内容重新生成为html格式
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

#监听评论内容的变化
db.event.listen(Comment.body, 'set', Comment.on_changed_body)


#关注
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #关注者id
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #被关注者id
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) #时间戳

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64)) #真实姓名(不同于用户名)
    location = db.Column(db.String(64)) #位置
    about_me = db.Column(db.Text()) #个人介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)    #注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)   #最后一次访问的时间
    email = db.Column(db.String(64), unique=True, index=True)   #电子邮箱
    nickname = db.Column(db.String(64))    #昵称
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  #角色id
    password_hash = db.Column(db.String(128))   #密码hash
    confirmed = db.Column(db.Boolean, default=False)    #是否已经确认账户
    headicon_url = db.Column(db.String(64)) #头像图标的url
    student = db.relationship('Student', backref='user', uselist=False) #通过Student的user字段拿到用户信息
    teacher = db.relationship('Teacher', backref='user', uselist=False) #通过Teacher的user字段拿到用户信息
    posts = db.relationship('Post', backref='author', lazy='dynamic') #该用户发布的动态
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic') #该用户发表的评论


    #关注的人的动态
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            #如果注册邮箱为指定的管理员邮箱，则角色确定为管理员
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            #如果不是，那么角色就是默认角色（学生）
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        #如果没有指定头像，则使用默认头像
        if self.headicon_url is None:
            self.headicon_url = 'resources/headicon/default.jpg'
        #自己关注自己，这是为了后续逻辑处理的方便
        self.follow(self)

    #遍历一次所有的用户，每个用户都要关注自己
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    #关注
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    #取消关注
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    #判断是否关注了用户
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    #是否被用户关注了
    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    #生成验证令牌，用于邮箱验证
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    #账户验证
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    #生成重设密码的token
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    #重设密码
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset')) #找到该token对应的用户
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    #生成更换邮箱的token
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    #更换邮箱地址
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        #判断新的邮箱地址有没有被其他人注册过
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User  %r>' % self.nickname

    #password字段是不可以读的
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    #设置password时通过generate_password_hash函数设置password_hash值
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    #验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #供login_manager使用，加载用户
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #是否具有某权限
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    #是否具有管理员权限
    def is_administrator(self):
        return self.can(Permission.ADMIN)


    #刷新最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()



#动态
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text) #动态内容
    body_html = db.Column(db.Text) #内容的html富文本形式
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #动态发布的时间戳
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) #作者id
    comments = db.relationship('Comment', backref='post', lazy='dynamic') #该动态对应的评论

    #每次动态内容更改，相应的body_html也要更改
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

#监听动态body更改
db.event.listen(Post.body, 'set', Post.on_changed_body)


'''
#消息表，用于聊天室使用
class Message(db.Model):
    __tablename__ = 'messages'
'''

'''
#资源表，用于记录每个课程对应资源的url
class Resource(db.Model):
    pass
'''