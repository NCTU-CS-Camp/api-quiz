from flask import jsonify
from .extensions import auth
from .models import User
from .extensions import db

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

@auth.error_handler
def auth_error(status):
    return jsonify({'error': '認證失敗', 'message': '無效的使用者名稱或密碼'}), status
