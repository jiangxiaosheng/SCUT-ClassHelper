# -*- coding: utf-8 -*-
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post, Comment, Teacher, Role

def generate():
    Role.insert_roles()
    users()
    posts()
    comments()
    teachers()


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
        if user.role.name != 'Student':
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
        if user.role.name != 'Teacher':
            index = randint(0, len(keys) - 1)
            teacher = Teacher(
                user_id=user.id,
                student_id=str(i).rjust(3, '0'),
                college=keys[index],
                major=colleges_majors[index],
                grade=grades[randint(0, len(grades) - 1)]
            )
            db.session.add(teacher)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:
                db.session.rollback()

def studentcourses(count=50):
    pass