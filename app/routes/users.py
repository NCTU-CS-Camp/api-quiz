from flask import Blueprint, jsonify, request, current_app as app
from ..extensions import auth, db, socketio, limiter
from ..models import User
from sqlalchemy.exc import IntegrityError
from flask_limiter.util import get_remote_address

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute", key_func=get_remote_address)
def create_user():
    data = request.get_json() or {}
    username = data.get('username'); password = data.get('password')
    
    app.logger.debug(f"Registration attempt for username: {username}")

    if not username or not password:
        app.logger.warning(f"Registration failed: missing parameters for {username}")
        return jsonify({'error':'缺少用戶名或密碼'}), 400
    if User.query.filter_by(username=username).first():
        app.logger.warning(f"Registration failed: user {username} already exists")
        return jsonify({'error':'用戶已存在'}), 409
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.debug(f"User {username} registered successfully")
        socketio.emit('new_user', {'username': username}, namespace='/')
        return jsonify({'message': '註冊成功'}), 201
    except IntegrityError:
        db.session.rollback()
        app.logger.error(f"Registration failed for {username} due to an integrity error (race condition).")
        return jsonify({'error': '用戶名已被註冊，請換一個再試'}), 409
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration failed for {username}: {str(e)}")
        return jsonify({'error': '註冊失敗', 'message': str(e)}), 500

@users_bp.route('/me', methods=['GET','PATCH','DELETE'])
@limiter.limit("20 per minute", methods=["PATCH", "DELETE"], key_func=get_remote_address)
@auth.login_required
def manage_current_user():
    user = auth.current_user()
    if not user:
        app.logger.error("User info request failed: no current user")
        return jsonify({'error': '未登入或無效的用戶'}), 401
    
    if request.method == 'GET':
        app.logger.debug(f"User {user.username} retrieved own account info")
        return jsonify(user.to_dict()), 200
    
    elif request.method == 'PATCH':
        data = request.get_json() or {}
        if 'username' in data:
            new_username = data['username']
            existing_user = User.query.filter(User.username == new_username, User.id != user.id).first()
            if existing_user:
                app.logger.warning(f"Update failed for {user.username}: new username {new_username} already exists.")
                return jsonify({'error': '用戶名已存在'}), 409
            user.username = new_username
        if 'password' in data:
            user.set_password(data['password'])
        if 'team' in data:
            user.team = data['team']

        iq_modified = 'iq' in data
        
        try:
            db.session.commit()
            app.logger.debug(f"User {user.username} updated account successfully")
            response_data = user.to_dict()
            message = 'IQ 沒辦法更新喔, 但其他已更新了' if iq_modified else '更新成功'
            return jsonify({'message': message, 'user': response_data}), 200
        except IntegrityError:
            db.session.rollback()
            app.logger.error(f"Account update failed for {user.username} due to an integrity error (e.g., race condition on username).")
            # 即使事前檢查了，這裡還是可能因為併發而出錯
            return jsonify({'error': '用戶名已被使用，請再試一次'}), 409 # 409 Conflict 更適合這種情況

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Account update failed for {user.username}: {str(e)}")
            return jsonify({'error': '更新失敗', 'message': str(e)}), 500


    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            app.logger.debug(f"User {user.username} deleted own account successfully")
            socketio.emit('delete_user', {'username': user.username}, namespace='/')
            return jsonify({'message': '帳號已刪除'}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Account deletion failed for {user.username}: {str(e)}")
            return jsonify({'error': '刪除失敗', 'message': str(e)}), 500


@users_bp.route('/count', methods=['GET'])
def total_users():
    """回傳目前 User table 的總筆數"""
    try:
        count = User.query.count()
        app.logger.debug(f"Total users: {count}")
        return jsonify({'count': count}), 200
    except Exception as e:
        app.logger.error(f"Failed to count users: {e}")
        return jsonify({'error': '查詢失敗', 'message': str(e)}), 500
