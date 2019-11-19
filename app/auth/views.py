from app.email import send_email
from . import auth
from .forms import LoginForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, \
    RegistrationForm
from ..models import User
from .. import db
from flask_login import login_user, current_user, logout_user, login_required
from flask import request, url_for, redirect, render_template, flash

#登录路由
@auth.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index') #登录成功返回主页
            return redirect(next)
        flash('邮箱地址或密码错误')
    return render_template('auth/login.html', form=form)


#登出路由
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    nickname=form.nickname.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


#请求钩子，在发送request前做预处理，包括调用ping函数更新最后访问时间，审核是否通过认证
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

#“未验证”路由
#如果用户不是匿名用户，且没有验证邮箱，则显示unconfirmed.html页面，否则重定向到主页
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


#重发验证邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认你的账户', 'auth/email/confirm', user=current_user, token=token)
    flash('一个新的确认邮件已经发送到你的邮箱')
    return redirect(url_for('main.index'))


#修改密码
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data): #确保旧密码是对的
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit() #将更新记录到数据库
            flash('你的密码更新成功')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template("auth/change_password.html", form=form)


#重设密码路由，用于“忘记密码”
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous: #这时候肯定是匿名用户，因为没有登录，如果能够登录的话就不用“忘记密码”了
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重新设置你的密码',
                       'auth/email/reset_password.html',
                       user=user, token=token)
        flash('一份关于重设密码的邮件已经发送到你的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


#用户点击重设密码邮件中的URL访问到该路由，显示重设密码的页面
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous: #判断是否是匿名用户
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('你的密码重置成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


#更改邮箱地址路由
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required #必须要登录
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data): #必须要正确输入密码
            new_email = form.email.data.lower() #先转换成小写，因为数据库中存的是小写的
            token = current_user.generate_email_change_token(new_email) #生成token
            send_email(new_email, '确认你的邮箱地址',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('一份有关更换邮箱地址的邮件已经发送到你的邮箱')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template("auth/change_email.html", form=form)


#用户点击更换邮箱地址的邮件中的URL后访问到该路由
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token): #如果更换成功，提交变化到数据库
        db.session.commit()
        flash('你的邮箱地址修改成功')
    else:
        flash('非法请求')
    return redirect(url_for('main.index'))