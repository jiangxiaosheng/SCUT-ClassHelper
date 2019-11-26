from flask import render_template
from . import forum
from ..api.forum import *

@forum.route('/')
def index():
    c = get_comments()
    for comment in c:
        print(Comment.from_json(comment))
    return render_template('forum/index.html')
