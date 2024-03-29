# -*- coding: utf-8 -*-
from flask import *
from flask_login import current_user, login_required
from app.models import User, Post
from . import main
from .forms import EditProfileForm
from .. import db
import os
from ..utils import md5, file_extension
from config import headicon_base_dir


#TODO:页面主页，对于不用用户应该有不同的设计
@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_anonymous:
        pass
    return render_template('index.html', is_login=False)


#用户资料页面
@main.route('/user/<email>')
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author_id=user.id).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False
    )
    posts = [item for item in pagination.items]
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


#修改个人资料路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        headicon = form.headicon.data #拿到表单中用户提交的头像文件
        headicon_name = current_user.email
        suffix = file_extension(headicon.filename) #后缀名，只能为jpg,gif等
        #存放头像文件的路径
        headicon_save_path = os.path.join(headicon_base_dir, md5(headicon_name)) + suffix #文件名用用户邮箱的md5重命名，并保存
        headicon.save(headicon_save_path) #保存
        current_user.headicon_url = md5(headicon_name) + suffix #修改user数据表的headicon_url字段
        current_user.about_me = form.about_me.data #修改个人介绍
        current_user.location = form.location.data #修改位置
        current_user.nickname = form.nickname.data #修改昵称
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('你的个人资料已经更新成功!')
        return redirect(url_for('.user', email=current_user.email))
    form.nickname.data = current_user.nickname
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


