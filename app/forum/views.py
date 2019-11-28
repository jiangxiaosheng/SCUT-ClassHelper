from flask import render_template
from . import forum
from ..api.forum import *
from flask_login import current_user

@forum.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False)
    posts = [item for item in pagination.items]
    return render_template('forum/index.html', posts=posts, pagination=pagination)
