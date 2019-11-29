# -*- coding: utf-8 -*-
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment, Teacher, Role, Student, Course, StudentCourse


def generate():
    Role.insert_roles()
    users()
    posts()
    comments()
    students()
    teachers()
    courses()
    studentcourses()


#测试用户
def memeshe():
    fake = Faker()
    user = User(
        email='437822838@qq.com',
        nickname='memeshe',
        password='yoga',
        confirmed=True,
        name='js',
        about_me='''僕が例えば他の人と結ばれたとして
        2人の間に命が宿ったとして
        その中にも君の遺伝子もそっと
        まぎれこんでいるだろう''',
        member_since=fake.past_date(),
        role=Role.query.filter_by(name='Student').first()
    )
    db.session.add(user)
    db.session.commit()
    student = Student(
        user_id=user.id,
        student_id='099',
        college='计算机学院',
        major='信息安全',
        grade='2017'
    )
    db.session.add(student)
    db.session.commit()
    i = 0
    course_count = Course.query.count()
    while i < 7:
        course = Course.query.offset(randint(0, course_count - 1)).first()
        record = StudentCourse(student_id='099', course_id=course.course_id)
        db.session.add(record)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    for i in range(20):
        p = Post(
            body=fake.text(),
            timestamp=fake.past_date(),
            author=user
        )
        db.session.add(p)
    db.session.commit()



def users(count=200):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 nickname=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def posts(count=150):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
        db.session.commit()

def comments(count=100):
    fake = Faker()
    i = 0
    user_count = User.query.count()
    post_count = Post.query.count()
    while i < count:
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post.query.offset(randint(0, post_count - 1)).first()
        c = Comment(
            body = fake.text(),
            timestamp = fake.past_date(),
            disabled = 0,
            author=u,
            post=p
        )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def teachers(count=20):
    colleges = ['计算机学院', '软件学院', '数学学院', '物理学院']
    positions = ['教授', '副教授', '讲师']
    i = 0
    user_count = User.query.count()
    while i < count:
        user = User.query.offset(randint(0, user_count - 1)).first()
        if user.role is None or user.role.name != 'Student':
            user.role = Role.query.filter_by(name='Teacher').first()
            teacher = Teacher(
                user_id=user.id,
                teacher_id=str(1000 + i),
                college=colleges[randint(0, len(colleges) - 1)],
                position=positions[randint(0, len(positions) - 1)]
            )
            db.session.add(teacher)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()


def students(count=30):
    colleges_majors = {
        '计算机学院': '信息安全',
        '软件学院': '软件工程',
        '数学学院': '应用数学',
        '物理学院': '理论物理'
    }
    keys = list(colleges_majors.keys())
    grades = ['2017', '2018', '2019']
    i = 0
    user_count = User.query.count()
    while i < count:
        user = User.query.offset(randint(0, user_count - 1)).first()
        if user.role is None or user.role.name != 'Teacher':
            user.role = Role.query.filter_by(name='Student').first()
            index = randint(0, len(keys) - 1)
            student = Student(
                user_id=user.id,
                student_id=str(i).rjust(3, '0'),
                college=keys[index],
                major=colleges_majors[keys[index]],
                grade=grades[randint(0, len(grades) - 1)]
            )
            db.session.add(student)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()

def studentcourses(count=50):
    i = 0
    student_count = Student.query.count()
    course_count = Course.query.count()
    while i < count:
        student = Student.query.offset(randint(0, student_count - 1)).first()
        course = Course.query.offset(randint(0, course_count - 1)).first()
        record = StudentCourse(student_id=student.student_id, course_id=course.course_id)
        db.session.add(record)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def courses(count=20):
    names = ['计算机网络', '操作系统', '分析力学', '电动力学', '数学分析', '实分析',
             '软件测试', '计算机图形学']
    teacher_count = Teacher.query.count()
    i = 0
    while i < count:
        t = Teacher.query.offset(randint(0, teacher_count - 1)).first()
        c = Course(
            course_id=str(201700 + i),
            name=names[randint(0, len(names) - 1)],
            teacher_id=t.teacher_id
        )
        db.session.add(c)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


