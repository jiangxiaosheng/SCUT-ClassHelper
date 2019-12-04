from flask import render_template
from . import forum
from ..api.forum import *
from flask_login import current_user
from .forms import *
from ..utils import localtime
from ..models import Post

@forum.route('/', methods=['GET', 'POST'])
def index():
    form = PublishPostForm()
    if form.validate_on_submit():
        p = Post(
            body=form.content.data,
            author_id=current_user.id,
            timestamp=localtime(),
        )
        form.content.data = ''
        db.session.add(p)
        db.session.commit()

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COURSE_PER_PAGE'],
        error_out=False)
    posts = [item for item in pagination.items]
    return render_template('forum/index.html', posts=posts, pagination=pagination, form=form)
