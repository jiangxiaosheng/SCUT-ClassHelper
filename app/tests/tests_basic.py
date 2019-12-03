import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Role
from app.email import send_email
from app.utils import *
from flask_mail import *
from .. import mail
from ..auth.forms import *

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
        #send_email('437822838@qq.com', 'hello', 'auth/email/testemail')
        msg = Message('hello', sender='123', recipients=['437822838@qq.com'])
        with self.app.app_context():
            mail.send(msg)

    def test_common(self):
        colleges_majors = {
            '计算机学院': '信息安全',
            '软件学院': '软件工程',
            '数学学院': '应用数学',
            '物理学院': '理论物理'
        }
        print((colleges_majors.keys()))

    def test_mysql(self):
        for i in range(201700, 201720):
            create_message_table(i)
        # insert_message(2, {
        #     'content': 'asd1',
        #     'user_id': '201',
        #     'course_id': '2'
        # })


    def test_localtime(self):
        print(localtime())


    def test_confirm_token(self):
        u = User.query.first()
        print(u.name)


    def test_form(self):
        form = StudentRegistrationForm()
        # print(StudentRegistrationForm.get_college_choices())
        print(form.major)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        # db.session.add(u)
        # db.session.commit()
        # token = u.generate_confirmation_token()
        # self.assertTrue(u.confirm(token))
        print(u.generate_confirmation_token())
        print(u.confirm('eyJhbGciOiJIUzUxMiIsImlhdCI6MTU3NTM2NDkxNCwiZXhwIjoxNTc1MzY4NTE0fQ.eyJjb25maXJtIjpudWxsfQ.T8v49ovjtT7hKGdru6qYCC18lfwyXBsz5UfIF3Qvhk7DDtpKGZLvLqbP9znzVolkNkbu9TOdDhqwpFLdIlRphA'))

    def test_re(self):
        if re.match(r'^[0-9]*$', '1'):
            print(True)
        else:
            print(False)

