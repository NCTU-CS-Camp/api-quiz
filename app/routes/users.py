from flask import Blueprint, jsonify, request, current_app as app
from ..extensions import auth, db, socketio
from ..models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username'); password = data.get('password')
    
    app.logger.debug(f"Registration attempt for username: {username}")

    if not username or not password:
        app.logger.warning(f"Registration failed: missing parameters for {username}")
        return jsonify({'error':'缺少參數'}), 400
    if User.query.filter_by(username=username).first():
        app.logger.warning(f"Registration failed: user {username} already exists")
        return jsonify({'error':'用戶已存在'}), 400
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.debug(f"User {username} registered successfully")
        socketio.emit('new_user', {'username': username}, namespace='/')
        return jsonify({'message': '註冊成功'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration failed for {username}: {str(e)}")
        return jsonify({'error': '註冊失敗', 'message': str(e)}), 500

@users_bp.route('/user', methods=['GET','PATCH','DELETE'])
@auth.login_required
def manage_user():
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
            user.username = data['username']
        if 'password' in data:
            user.set_password(data['password'])
        if 'team' in data:
            user.team = data['team']
        if 'iq' in data:
            user.iq = data['iq']
        
        try:
            db.session.commit()
            app.logger.debug(f"User {user.username} updated account successfully")
            return jsonify(user.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Account update failed for {user.username}: {str(e)}")
            return jsonify({'error': '更新失敗', 'message': str(e)}), 500


    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            app.logger.debug(f"User {user.username} deleted own account successfully")
            return jsonify({'message': '帳號已刪除'}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Account deletion failed for {user.username}: {str(e)}")
            return jsonify({'error': '刪除失敗', 'message': str(e)}), 500

    
