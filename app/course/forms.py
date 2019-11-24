# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, Length


class JoinCourseForm(FlaskForm):
    id = StringField("课程id", validators=[DataRequired(), Length(1, 12)])
    submit = SubmitField("查询")
