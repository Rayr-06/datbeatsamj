from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
    # Check if teacher exists, if not create one
    if not User.query.filter_by(role='teacher').first():
        teacher = User(
            email='teacher@example.com',
            name='Teacher Name',
            password_hash=generate_password_hash('admin123'),
            role='teacher'
        )
        db.session.add(teacher)
        db.session.commit()
        print('Teacher account created: email=teacher@example.com, password=admin123')
    else:
        print('Database already initialized.')