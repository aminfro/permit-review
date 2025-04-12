from app import app, db, User


with app.app_context():
    admin = User(
        username='admin',
        full_name='Admin User',
        role='admin',
        discipline='General'
    )
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()
