from app import create_app
from app.extensions import db, socketio
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9000, debug=False)
