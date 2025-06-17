from flask import jsonify, current_app as app
from .extensions import auth
from .models import User
from .extensions import db

@auth.verify_password
def verify_password(username, password):
    app.logger.debug(f"Authentication attempt for user: {username}")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        app.logger.info(f"Authentication successful for user: {username}")
        return user    # 回傳 User 物件
    app.logger.warning(f"Authentication failed for user: {username}")
    return None        # 驗證失敗

@auth.error_handler
def auth_error(status):
    return jsonify({'error': '認證失敗', 'message': '無效的使用者名稱或密碼'}), status
