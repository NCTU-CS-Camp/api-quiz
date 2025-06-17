from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

app = Flask(__name__)

# ===== Logger Configuration =====
def setup_logger():
    """設定應用程式 logger"""
    # 建立 logs 資料夾
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 設定 logger 格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # 檔案 handler (輪轉日誌，最大 10MB，保留 10 個檔案)
    file_handler = RotatingFileHandler(
        'logs/api.log', maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # 設定 app logger
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # 避免重複記錄
    app.logger.propagate = False

setup_logger()

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# ===== Request/Response Logging Middleware =====
@app.before_request
def log_request_info():
    """記錄請求資訊"""
    app.logger.info(f"Request: {request.method} {request.path}")
    app.logger.debug(f"Request headers: {dict(request.headers)}")
    if request.is_json:
        app.logger.debug(f"Request JSON: {request.get_json()}")
    elif request.form:
        app.logger.debug(f"Request form: {dict(request.form)}")

@app.after_request
def log_response_info(response):
    """記錄回應資訊"""
    app.logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

# ===== Models =====
class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    team          = db.Column(db.Integer, default=0)
    iq         = db.Column(db.Integer, default=0)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
        app.logger.debug(f"Password set for user: {self.username}")

    def check_password(self, pw):
        result = check_password_hash(self.password_hash, pw)
        app.logger.debug(f"Password check for user {self.username}: {'success' if result else 'failed'}")
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'team': self.team,
            'iq': self.iq,
        }
        
# ===== HTTP Basic Auth =====
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
    app.logger.warning(f"Authentication error: {status}")
    return jsonify({'error': '認證失敗', 'message': '無效的使用者名稱或密碼'}), status

# ===== Error Handlers =====
@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 Error: {request.method} {request.path} not found")
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
    app.logger.warning(f"405 Error: Method {request.method} not allowed for {request.path}")
    return jsonify({
        'error': 'HTTP 方法不允許',
        'message': f'路由 {request.path} 不支援 {request.method} 方法',
        'allowed_methods': error.description if hasattr(error, 'description') else []
    }), 405

@app.errorhandler(400)
def bad_request(error):
    app.logger.warning(f"400 Error: Bad request - {error.description}")
    return jsonify({
        'error': '請求錯誤',
        'message': str(error.description) if hasattr(error, 'description') else '請求格式錯誤'
    }), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 Error: Internal server error - {str(error)}")
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
            app.logger.debug("No current user found")
            return None
        db_user = User.query.get(user.id)
        if db_user:
            app.logger.debug(f"Current user: {db_user.username}")
        else:
            app.logger.warning(f"User ID {user.id} not found in database")
        return db_user
    except Exception as e:
        app.logger.error(f"Error getting current user: {str(e)}")
        return None

# ===== question Endpoints =====
@app.route('/questions', methods=['GET'])
@auth.login_required
def get_questions():
    user = get_current_user_safe()
    app.logger.info(f"User {user.username if user else 'Unknown'} requested questions list")
    return jsonify({'message': '總共有5個問題，用 /questions/<id> 取得問題內容'}), 200

@app.route('/questions/<int:id>', methods=['GET'])
@auth.login_required
def get_question(id):
    user = get_current_user_safe()
    app.logger.info(f"User {user.username if user else 'Unknown'} requested question {id}")
    
    try:
        with open(f'questions/Q{id}.txt', 'r', encoding='utf-8') as f:
            question = f.read()
        app.logger.debug(f"Successfully loaded question {id}")
        return jsonify({'id': id, 'question': question}), 200
    except FileNotFoundError:
        app.logger.warning(f"Question file Q{id}.txt not found")
        return jsonify({'error': '問題不存在', 'message': f'找不到問題 {id}'}), 404
    except Exception as e:
        app.logger.error(f"Error reading question {id}: {str(e)}")
        return jsonify({'error': '讀取問題失敗', 'message': str(e)}), 500

@app.route('/questions/<int:id>', methods=['POST'])
@auth.login_required
def answer_question(id):
    user = get_current_user_safe()
    if not user:
        app.logger.error("No user found when answering question")
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    app.logger.info(f"User {user.username} attempting to answer question {id}")
    
    data = request.get_json() or {}
    answer = data.get('answer')
    if not answer:
        app.logger.warning(f"User {user.username} submitted empty answer for question {id}")
        return jsonify({'error': '缺少參數', 'message': '請提供答案'}), 400
    
    try:
        with open(f'questions/Ans{id}.txt', 'r', encoding='utf-8') as f:
            correct_answer = f.read().strip()
        app.logger.debug(f"Loaded correct answer for question {id}")
    except FileNotFoundError:
        app.logger.error(f"Answer file Ans{id}.txt not found")
        return jsonify({'error': '答案檔案不存在', 'message': f'找不到問題 {id} 的答案檔案'}), 404
    except Exception as e:
        app.logger.error(f"Error reading answer for question {id}: {str(e)}")
        return jsonify({'error': '讀取答案失敗', 'message': str(e)}), 500
    
    if answer.strip() == correct_answer:
        old_iq = user.iq
        user.iq += 10
        db.session.commit()
        app.logger.info(f"User {user.username} answered question {id} correctly. IQ: {old_iq} -> {user.iq}")
        return jsonify({'message': '回答正確！你的 IQ 增加了 10', 'new_iq': user.iq}), 200
    else:
        app.logger.info(f"User {user.username} answered question {id} incorrectly")
        return jsonify({'error': '回答錯誤', 'message': '答案不正確，請再試一次'}), 400

# ===== Admin Endpoints =====

# ===== User Endpoints =====
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    app.logger.info(f"Registration attempt for username: {username}")
    
    if not username or not password:
        app.logger.warning(f"Registration failed: missing parameters for {username}")
        return jsonify({'error': '缺少參數', 'message': '請提供 username 和 password'}), 400
    if User.query.filter_by(username=username).first():
        app.logger.warning(f"Registration failed: username {username} already exists")
        return jsonify({'error': '用戶已存在', 'message': '使用者名稱已存在'}), 400
    
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"User {username} registered successfully")
        return jsonify({'message': '註冊成功'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration failed for {username}: {str(e)}")
        return jsonify({'error': '註冊失敗', 'message': str(e)}), 500

@app.route('/user', methods=['GET'])
@auth.login_required
def get_my_account():
    user = get_current_user_safe()
    if not user:
        app.logger.error("User info request failed: no current user")
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    app.logger.info(f"User {user.username} retrieved own account info")
    return jsonify(user.to_dict()), 200


@app.route('/user', methods=['PATCH'])
@auth.login_required
def update_my_account():
    user = get_current_user_safe()
    if not user:
        app.logger.error("Account update failed: no current user")
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    data = request.get_json() or {}
    username = data.get('username')
    team = data.get('team')
    iq = data.get('iq')

    if username:
        if User.query.filter_by(username=username).first() and username != user.username:
            app.logger.warning(f"Username {username} already exists for update")
            return jsonify({'error': '用戶已存在', 'message': '使用者名稱已存在'}), 400
        user.username = username
        app.logger.info(f"User {user.username} updated username to {username}")
    
    if team is not None:
        user.team = team
        app.logger.info(f"User {user.username} updated team to {team}")
    
    if iq is not None:
        user.iq = iq
        app.logger.info(f"User {user.username} updated IQ to {iq}")

    try:
        db.session.commit()
        app.logger.info(f"User {user.username} updated account successfully")
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Account update failed for {user.username}: {str(e)}")
        return jsonify({'error': '更新失敗', 'message': str(e)}), 500


@app.route('/user', methods=['DELETE'])
@auth.login_required
def delete_my_account():
    user = get_current_user_safe()
    if not user:
        app.logger.error("Account deletion failed: no current user")
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    username = user.username
    app.logger.info(f"User {username} attempting to delete own account")
    
    try:
        db.session.delete(user)
        db.session.commit()
        app.logger.info(f"User {username} deleted own account successfully")
        return jsonify({'message': '帳號已刪除'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Account deletion failed for {username}: {str(e)}")
        return jsonify({'error': '刪除失敗', 'message': str(e)}), 500

@app.route('/user/iq', methods=['GET'])
@auth.login_required
def get_my_iq():
    user = get_current_user_safe()
    if not user:
        app.logger.error("IQ request failed: no current user")
        return jsonify({'error': '用戶不存在', 'message': '找不到當前用戶'}), 404
    
    app.logger.info(f"User {user.username} checked IQ: {user.iq}")
    return jsonify({'iq': user.iq}), 200

if __name__ == '__main__':
    app.logger.info("Starting Flask application...")
    
    with app.app_context():
        db.create_all()
        # 建立 admin 帳號（如不存在）
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Admin account created")
        else:
            app.logger.info("Admin account already exists")
    
    app.logger.info("Flask application started on http://0.0.0.0:9000")
    app.run(host='0.0.0.0', port=9000, debug=True)
