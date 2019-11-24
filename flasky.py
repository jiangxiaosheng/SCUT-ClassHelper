# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Role, Permission, User, Student, Teacher, StudentCourse, Course
from flask_migrate import Migrate
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, Permission=Permission, User=User, Student=Student, Teacher=Teacher,
                StudentCourse=StudentCourse, Course=Course)

def page_filter(class_list):
    l = class_list
    out = []
    for i in range(len(l)):
        if i % 9 == 0:
            out.append(l[i])
    return out

if __name__ == '__main__':
    app.add_template_filter(page_filter, 'page_filter')
    app.run(debug=True)
