from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class JoinCourseForm(FlaskForm):
    id = StringField("课程id", validators=[DataRequired(), Length(1, 12)])
    submit = SubmitField("查询")