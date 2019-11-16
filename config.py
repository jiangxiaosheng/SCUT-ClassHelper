import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = "scutse" #密钥
    MAIL_SERVER = 'smtp.qq.com' #用qq邮箱发送邮件
    MAIL_PORT = 587 #qq邮箱的端口
    MAIL_USE_TLS = True #安全加密传输
    MAIL_USERNAME = '437822838@qq.com' #发送者的邮箱
    MAIL_PASSWORD = 'vofqflldbcnrcbaf' #qq邮箱的smtp服务的口令
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]' #邮件主题
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}