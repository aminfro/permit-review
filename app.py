from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Permit, PermitDrawing, PermitAttachment, PermitReview
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///permit.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {'pdf', 'dwg', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user.set_password(new_password)
        db.session.commit()
        flash("Password reset successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('reset_password.html', user=user)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
    elif user.username == current_user.username:
        flash("You cannot delete yourself.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' has been deleted.", "success")

    return redirect(url_for('dashboard'))

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form['role']
        discipline = request.form['discipline']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('create_user'))

        new_user = User(
            username=username,
            full_name=full_name,
            role=role,
            discipline=discipline
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('create_user.html')




@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/view_permit/<int:permit_id>')
@login_required
def view_permit(permit_id):
    permit = Permit.query.get_or_404(permit_id)

    # Only the contractor who created it OR an inspector can view it
    if current_user.role == 'contractor' and permit.contractor_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    reviews = PermitReview.query.filter_by(permit_id=permit.id).all()
    return render_template('view_permit.html', permit=permit, reviews=reviews)
@app.route('/contractor_review/<int:permit_id>', methods=['GET', 'POST'])
@login_required
def contractor_review(permit_id):
    if current_user.role != 'contractor':
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    permit = Permit.query.get_or_404(permit_id)

    # check if already reviewed
    existing = ContractorReview.query.filter_by(permit_id=permit.id, contractor_id=current_user.id).first()

    if request.method == 'POST':
        status = request.form['status']
        comment = request.form['comment']

        if existing:
            existing.status = status
            existing.comment = comment
            existing.reviewed_at = datetime.utcnow()
        else:
            new_review = ContractorReview(
                permit_id=permit.id,
                contractor_id=current_user.id,
                status=status,
                comment=comment
            )
            db.session.add(new_review)

        db.session.commit()

        # ✅ Check if all contractor reviewers have approved
        required_users = User.query.filter_by(role='contractor', discipline=permit.discipline).all()
        approved = all(
            ContractorReview.query.filter_by(permit_id=permit.id, contractor_id=u.id, status='approved').first()
            for u in required_users
        )

        if approved:
            permit.status = 'contractor_supervisor_review'
            db.session.commit()
            flash("All contractor disciplines approved. Sent to supervisor.", "success")
        else:
            flash("Your review has been recorded.", "info")

        return redirect(url_for('dashboard'))

    all_reviews = ContractorReview.query.filter_by(permit_id=permit.id).all()
    return render_template('contractor_review.html', permit=permit, reviews=all_reviews, existing_review=existing)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    permits = []
    users = []
    new_permits = []
    reviewed_permits = []

    if current_user.role == 'contractor':
        all_pending = Permit.query.filter_by(status='contractor_review').all()

        permits = []
        for permit in all_pending:
            already_reviewed = ContractorReview.query.filter_by(
                permit_id=permit.id,
                contractor_id=current_user.id
            ).first()

            if not already_reviewed:
                permits.append(permit)

    elif current_user.role == 'inspector':
        discipline_permits = Permit.query.filter_by(status='inspector_review').all()

        new_permits = []
        reviewed_permits = []

        for permit in discipline_permits:
            reviewed_by_this_inspector = any(
                review.inspector_id == current_user.id for review in permit.reviews
            )
            if reviewed_by_this_inspector:
                reviewed_permits.append(permit)
            else:
                new_permits.append(permit)

        permits = discipline_permits

    elif current_user.role == 'admin':
        permits = Permit.query.all()
        users = User.query.all()

    return render_template(
        'dashboard.html',
        user=current_user,
        permits=permits,
        users=users,
        new_permits=new_permits,
        reviewed_permits=reviewed_permits,
    )

@app.route('/review_permit/<int:permit_id>', methods=['GET', 'POST'])
@login_required
def review_permit(permit_id):
    if current_user.role != 'inspector':
        flash("Only inspectors can review permits.", "danger")
        return redirect(url_for('dashboard'))

    permit = Permit.query.get_or_404(permit_id)

    # Check if this inspector is allowed (discipline match)
    if permit.discipline != current_user.discipline:
        flash("This permit is not in your discipline.", "warning")
        return redirect(url_for('dashboard'))

    # Check if inspector has already reviewed
    existing_review = PermitReview.query.filter_by(permit_id=permit.id, inspector_id=current_user.id).first()

    if request.method == 'POST':
        status = request.form['status']
        comment = request.form['comment']

        if existing_review:
            existing_review.status = status
            existing_review.comment = comment
            existing_review.reviewed_at = datetime.utcnow()
        else:
            review = PermitReview(
                permit_id=permit.id,
                inspector_id=current_user.id,
                status=status,
                comment=comment
            )
            db.session.add(review)

        db.session.commit()
        flash("Your review has been submitted.", "success")
        return redirect(url_for('dashboard'))

    all_reviews = PermitReview.query.filter_by(permit_id=permit.id).all()
    return render_template('review_permit.html', permit=permit, reviews=all_reviews, existing_review=existing_review)


    return render_template('dashboard.html', user=current_user, permits=permits, users=users if current_user.role == 'admin' else [])
@app.route('/submit_permit', methods=['GET', 'POST'])
@login_required
def submit_permit():
    if current_user.role != 'contractor':
        flash("Only contractors can submit permits.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        discipline = request.form['discipline']
        title = request.form['title']
        description = request.form['description']
        work_area = request.form['work_area']

        last_permit = Permit.query.filter_by(contractor_id=current_user.id).order_by(Permit.permit_number.desc()).first()
        next_number = last_permit.permit_number + 1 if last_permit else 1

        permit = Permit(
            contractor_id=current_user.id,
            permit_number=next_number,
            discipline=discipline,
            title=title,
            description=description,
            work_area=work_area
        )
        db.session.add(permit)
        db.session.commit()

        # Drawings
        index = 0
        while True:
            key_drw = f'drawing_number_{index}'
            key_rev = f'revision_{index}'
            key_desc = f'drawing_desc_{index}'
            if key_drw in request.form:
                drawing = PermitDrawing(
                    permit_id=permit.id,
                    drawing_number=request.form[key_drw],
                    revision=request.form[key_rev],
                    description=request.form.get(key_desc)
                )
                db.session.add(drawing)
                index += 1
            else:
                break

        # Attachments
        files = request.files.getlist('attachments')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)

                attachment = PermitAttachment(
                    permit_id=permit.id,
                    filename=filename,
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    file_path=filepath
                )
                db.session.add(attachment)

        db.session.commit()
        flash("Permit submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('submit_permit.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
