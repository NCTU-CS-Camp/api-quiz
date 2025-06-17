from flask import Flask, jsonify, request
from .config     import Config
from .extensions import db, auth
import app.auth # 初始化 auth 
from .logger     import setup_logger
from .routes.questions import questions_bp
from .routes.users     import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    setup_logger(app)
    db.init_app(app)
    
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

    # register blueprints
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)
    
    # Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"400 Error: Bad request - {error.description}")
        return jsonify({
            'error': '請求錯誤',
            'message': str(error.description) if hasattr(error, 'description') else '請求格式錯誤'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f"401 Error: Unauthorized access - {error.description}")
        return jsonify({
            'error': '未授權',
            'message': str(error.description) if hasattr(error, 'description') else '需要登入或無效的認證'
        }), 401
    
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

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Error: Internal server error - {str(error)}")
        db.session.rollback()
        return jsonify({
            'error': '伺服器內部錯誤',
            'message': '伺服器發生未預期的錯誤，請稍後再試'
        }), 500

    return app
