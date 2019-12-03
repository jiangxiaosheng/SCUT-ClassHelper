# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, Length

#查询课程表单
class JoinCourseForm(FlaskForm):
    id_or_name = StringField("课程id或课程名", validators=[DataRequired(), Length(1, 12)])
    submit = SubmitField("查询")


#发布公告表单
class AnnouncementForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(1, 20)])
    content = StringField("内容", validators=[DataRequired(), Length(1, 300)])
    submit = SubmitField("发布")


