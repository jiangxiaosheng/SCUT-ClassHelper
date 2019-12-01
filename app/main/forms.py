# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length


class EditProfileForm(FlaskForm):
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('个人介绍')
    nickname = StringField('昵称', validators=[Length(0, 12)])
    headicon = FileField('上传头像', validators=[FileRequired(), FileAllowed(['jpg','jpeg','png','gif'])])
    submit = SubmitField('确定')

