from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# ===== Models =====
class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    iq            = db.Column(db.Integer, nullable=True, default=0)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'iq': self.iq}

# ===== HTTP Basic Auth =====
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user    # 回傳 User 物件
    return None        # 驗證失敗

@auth.error_handler
def auth_error(status):
    return jsonify({'error': '認證失敗', 'message': '無效的使用者名稱或密碼'}), status

# ===== Error Handlers =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': '路由不存在', 
        'message': f'找不到路由 {request.method} {request.path}',
        'available_routes': [
            'GET /questions',
            'GET /questions/<id>',
            'POST /questions/<id>/answer',
            'POST /register',
            'GET /user',
            'DELETE /user',
            'GET /user/iq'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'HTTP 方法不允許',
        'message': f'路由 {request.path} 不支援 {request.method} 方法',
        'allowed_methods': error.description if hasattr(error, 'description') else []
    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': '請求錯誤',
        'message': str(error.description) if hasattr(error, 'description') else '請求格式錯誤'
    }), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'error': '伺服器內部錯誤',
        'message': '伺服器發生未預期的錯誤，請稍後再試'
    }), 500

# ===== Helper Function =====
def get_current_user_safe():
    """安全地取得當前用戶，如果不存在則回傳 None"""
    try:
        user = auth.current_user()
        if user is None:
            return None
        return User.query.get(user.id)
    except:
        return None

# ===== question Endpoints =====
@app.route('/questions', methods=['GET'])
@auth.login_required
def get_questions():
    return jsonify({'message': '總共有5個問題，用 /questions/<id> 取得問題內容'}), 200

@app.route('/questions/<int:id>', methods=['GET'])
@auth.login_required
def get_question(id):
    try:
        with open(f'questions/Q{id}.txt', 'r', encoding='utf-8') as f:
            question = f.read()
        return jsonify({'id': id, 'question': question}), 200
    except FileNotFoundError:
        return jsonify({'error': '問題不存在', 'message': f'找不到問題 {id}'}), 404
    except Exception as e:
        return jsonify({'error': '讀取問題失敗', 'message': str(e)}), 500

@app.route('/questions/<int:id>', methods=['POST'])
@auth.login_required
def answer_question(id):
    user = get_current_user_safe()
    if not user:
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    data = request.get_json() or {}
    answer = data.get('answer')
    if not answer:
        return jsonify({'error': '缺少參數', 'message': '請提供答案'}), 400
    
    try:
        with open(f'questions/Ans{id}.txt', 'r', encoding='utf-8') as f:
            correct_answer = f.read().strip()
    except FileNotFoundError:
        return jsonify({'error': '答案檔案不存在', 'message': f'找不到問題 {id} 的答案檔案'}), 404
    except Exception as e:
        return jsonify({'error': '讀取答案失敗', 'message': str(e)}), 500
    
    if answer.strip() == correct_answer:
        user.iq += 10
        db.session.commit()
        return jsonify({'message': '回答正確！你的 IQ 增加了 10', 'new_iq': user.iq}), 200
    else:
        return jsonify({'error': '回答錯誤', 'message': '答案不正確，請再試一次'}), 400

# ===== Admin Endpoints =====
@app.route('/admin/users', methods=['GET'])
@auth.login_required
def get_all_users():
    user = get_current_user_safe()
    if not user or user.username != 'admin':
        return jsonify({'error': '權限不足', 'message': '只有管理員可以執行此操作'}), 403
    
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    current_user = get_current_user_safe()
    if not current_user or current_user.username != 'admin':
        return jsonify({'error': '權限不足', 'message': '只有管理員可以執行此操作'}), 403
    
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'error': '用戶不存在', 'message': f'找不到 ID 為 {user_id} 的用戶'}), 404
    
    if user_to_delete.username == 'admin':
        return jsonify({'error': '操作不允許', 'message': '不能刪除管理員帳號'}), 400
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'message': f'用戶 {user_to_delete.username} 已被刪除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '刪除失敗', 'message': str(e)}), 500
    
    
# ===== User Endpoints =====
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '缺少參數', 'message': '請提供 username 和 password'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用戶已存在', 'message': '使用者名稱已存在'}), 400
    
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '註冊成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '註冊失敗', 'message': str(e)}), 500

@app.route('/user', methods=['GET'])
@auth.login_required
def get_my_account():
    user = get_current_user_safe()
    if not user:
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    return jsonify(user.to_dict()), 200

@app.route('/user', methods=['DELETE'])
@auth.login_required
def delete_my_account():
    user = get_current_user_safe()
    if not user:
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '帳號已刪除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '刪除失敗', 'message': str(e)}), 500

@app.route('/user/iq', methods=['GET'])
@auth.login_required
def get_my_iq():
    user = get_current_user_safe()
    if not user:
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    return jsonify({'iq': user.iq}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 建立 admin 帳號（如不存在）
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=9000, debug=True)
