from .errors import forbidden, internal_error
from .. import db
from . import api
from ..models import Comment, Post, Permission, PostLike
from flask import request, current_app, url_for, jsonify, g
from ..utils import localtime


#获取所有评论
@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })



#获取对应某一id的评论
@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


#获取某一条动态的所有评论
@api.route('/posts/comments')
def get_post_comments():
    id = request.args.get('id')
    if id is None:
        return internal_error('Please check your url.')
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

#点赞
@api.route('/posts/like', methods=['POST'])
def like_post():
    post_id = request.values.get('post_id')
    user_id = request.values.get('user_id')
    post = Post.query.filter_by(id=post_id).first()
    record = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
    if record is None: #如果没有点过赞，则新建一条记录
        record = PostLike(user_id=user_id, post_id=post_id, like=1)
    else:
        record.like = not record.like
    db.session.add(record)
    db.session.commit()
    return jsonify({"count": post.liked_count})


@api.route('/comments/publish', methods=['POST'])
def publish_comment():
    post_id = request.values.get("post_id")
    user_id = request.values.get("user_id")
    content = request.values.get("content")
    timestamp = localtime()
    c = Comment(
        author_id=user_id,
        post_id=post_id,
        body=content,
        timestamp=timestamp,
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({
        "flag": True,
        "timestamp": timestamp,
    })

'''
@api.route('/posts/<int:id>/comments/', methods=['POST'])
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
        {'Location': url_for('api.get_comment', id=comment.id)}



@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}


@api.route('/posts/<int:id>', methods=['PUT'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())'''
