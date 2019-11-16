from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

#装饰器，审查是否具有相应的权限
#permission:例如Permission.WRITE, Permission.ADMIN等
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#装饰器，审查是否具有管理员权限
def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
