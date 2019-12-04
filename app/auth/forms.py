# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, form, fields
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


#教师注册表单
class TeacherRegistrationForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    nickname = StringField('昵称', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])

    college_choices = [(1, '计算机学院'), (2, '软件学院'), (3, '数学学院'), (4, '物理学院')]
    position_choices = [(1, '教授'), (2, '副教授'), (3, '讲师')]
    college = SelectField(
        label='学院',
        validators=[DataRequired('请选择学院')],
        choices=college_choices,
        coerce=int
    )
    position = SelectField(
        label='职位',
        validators=[DataRequired('请选择职位')],
        choices=position_choices,
        coerce=int
    )

    submit = SubmitField('注册')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被使用!')

    @staticmethod
    def get_college(i):
        return TeacherRegistrationForm.college_choices[i - 1][1]

    @staticmethod
    def get_position(i):
        return TeacherRegistrationForm.position_choices[i - 1][1]



#学生注册表单
class StudentRegistrationForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
    nickname = StringField('昵称', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])

    college_choices = [(1, '计算机学院'), (2, '软件学院'), (3, '数学学院'), (4, '物理学院')]
    major_choices = [
        (1, '信息安全'), (2, '网络工程'), (3, '计算机联合班'), (4, '计算机创新班'),
        (5, '软件工程'), (6, '软件工程(中澳班)'), (7, '软件工程(卓越班)'),
        (8, '应用数学'), (9, '统计学'), (10, '信息与计算科学'),
        (11, '应用物理'), (12, '核物理'), (13, '天体物理')
    ]

    grade_choices = [(1, '2017'), (2, '2018'), (3, '2019')]

    college = SelectField(
        label='学院',
        validators=[DataRequired('请选择学院')],
        choices=college_choices,
        coerce=int
    )

    major = SelectField(
        label='专业',
        validators=[DataRequired('请选择专业')],
        choices=major_choices,
        coerce=int
    )

    grade = SelectField(
        label='年级',
        validators=[DataRequired('请选择年级')],
        choices=grade_choices,
        coerce=int
    )

    submit = SubmitField("注册")

    @staticmethod
    def get_college(i):
        return StudentRegistrationForm.college_choices[i - 1][1]

    @staticmethod
    def get_grade(i):
        return StudentRegistrationForm.grade_choices[i - 1][1]

    @staticmethod
    def get_major(i):
        return StudentRegistrationForm.major_choices[i - 1][1]

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被使用!')







class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('确认新密码',
                              validators=[DataRequired()])
    submit = SubmitField('修改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱地址', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更新邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被使用过')


