from app import app, db, User

with app.app_context():
    user = User(
        username='shakiba',
        full_name='Amin Amiri',
        role='contractor'  # یا 
    )
    user.set_password('123456')  # پسورد دلخواهت
    db.session.add(user)
    db.session.commit()
    print("User created successfully!")
existing_user = User.query.filter_by(username=username).first()
if existing_user:
    flash("Username already exists.", "danger")
    return redirect(url_for('create_user'))
