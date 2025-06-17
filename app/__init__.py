from flask import Flask
from .config     import Config
from .extensions import db, auth
from .logger     import setup_logger
from .routes.questions import questions_bp
from .routes.users     import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    setup_logger(app)
    db.init_app(app)

    # register blueprints
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)

    # error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error':'路由不存在'}, 404

    return app
