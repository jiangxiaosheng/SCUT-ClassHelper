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


if __name__ == '__main__':
    app.run(debug=True)
