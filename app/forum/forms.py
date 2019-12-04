from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class PublishPostForm(FlaskForm):
    content = TextAreaField("写点什么吧", validators=[DataRequired('请填写内容'), Length(1, 300, '字数超过限制')])
    submit = SubmitField("发布")