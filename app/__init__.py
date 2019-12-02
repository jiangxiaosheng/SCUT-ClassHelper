# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config, DevelopmentConfig
import pymysql


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
#开发用数据库
message_db = pymysql.connect("localhost", DevelopmentConfig.MYSQL_USERNAME, DevelopmentConfig.MYSQL_PASSWORD, 'SCUT_ClassHelper')
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .course import course as course_blueprint
    app.register_blueprint(course_blueprint, url_prefix='/course')

    from .forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint, url_prefix='/forum')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
