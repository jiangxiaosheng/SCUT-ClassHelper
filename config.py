# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))
resources_base_dir = os.path.join(basedir, 'app', 'static', 'resources')
headicon_base_dir = os.path.join(basedir, 'app', 'static', 'headicon')

class Config():
    SECRET_KEY = "scutse" #密钥
    MAIL_SERVER = 'smtp.qq.com' #用qq邮箱发送邮件
    MAIL_PORT = 587 #qq邮箱的端口
    MAIL_USE_TLS = True #安全加密传输
    MAIL_USERNAME = '437822838@qq.com' #发送者的邮箱
    MAIL_PASSWORD = 'gjqtpbnbyvuabidg' #qq邮箱的smtp服务的口令
    FLASKY_MAIL_SUBJECT_PREFIX = '[SCUT-ClassHelper]' #邮件主题
    FLASKY_MAIL_SENDER = 'SCUT-ClassHelper Admin <437822838@qq.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_COURSE_PER_PAGE = 9
    FLASKY_COMMENTS_PER_PAGE = 7
    FLASKY_POSTS_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = 'root'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite://'


class ProductionConfig(Config):
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = 'd3R5ha9C7aXl'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}