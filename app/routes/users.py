from flask import Blueprint, jsonify, request
from ..extensions import auth, db
from ..models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username'); password = data.get('password')
    if not username or not password:
        return jsonify({'error':'缺少參數'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error':'用戶已存在'}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user); db.session.commit()
    return jsonify({'message':'註冊成功'}), 201

@users_bp.route('/user', methods=['GET','PATCH','DELETE'])
@auth.login_required
def manage_user():
    user = auth.current_user()
    if request.method == 'GET':
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
        db.session.commit()
        return jsonify({'message':'用戶資料已更新'}), 200

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message':'用戶已刪除'}), 200
    
