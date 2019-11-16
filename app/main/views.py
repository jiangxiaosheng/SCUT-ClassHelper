from flask import *
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    #TODO: 主页
    return render_template('index.html')
