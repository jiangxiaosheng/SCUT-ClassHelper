from flask import render_template
from . import forum

@forum.route('/')
def index():
    return render_template('forum/index.html')
