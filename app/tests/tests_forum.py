import unittest
from ..api.forum import get_comments
from app import create_app, db
from ..fake import *


class ForumTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        users()
        posts()
        comments()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_comments_json(self):
        comments = get_comments(1)
        for c in comments:
            print(c)