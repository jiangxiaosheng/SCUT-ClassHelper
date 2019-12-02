import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Role
from app.email import send_email
from app.utils import *

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #app是否生成
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    #app是test模式
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    #设置password属性时应该设置了password_hash
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    # password属性应该是只写的
    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    # 密码验证功能
    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    # 加盐hash
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_send_email(self):
        user = User.query.filter_by(username='memeshe').first()
        send_email('3422290299@qq.com', 'Confirm your account', 'auth/email/confirm', user=user)

    def test_common(self):
        colleges_majors = {
            '计算机学院': '信息安全',
            '软件学院': '软件工程',
            '数学学院': '应用数学',
            '物理学院': '理论物理'
        }
        print((colleges_majors.keys()))

    def test_mysql(self):
        #create_message_table(201702)
        insert_message(201701, {
            'content': 'asd1',
            'user_id': '201',
            'course_id': '201701'
        })


    def test_localtime(self):
        print(localtime())
