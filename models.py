from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20))
    full_name = db.Column(db.String(150))
    discipline = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class ContractorReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permit_id = db.Column(db.Integer, db.ForeignKey('permit.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20))  # 'approved' or 'rejected'
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    permit = db.relationship('Permit', backref='contractor_reviews')
    contractor = db.relationship('User')

class Permit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permit_number = db.Column(db.Integer)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discipline = db.Column(db.String(50))
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    work_area = db.Column(db.String(150))
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='submitted')

    contractor = db.relationship('User')
class PermitDrawing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permit_id = db.Column(db.Integer, db.ForeignKey('permit.id'))
    drawing_number = db.Column(db.String(50))
    revision = db.Column(db.String(10))
    description = db.Column(db.String(200))

    permit = db.relationship('Permit', backref='drawings')


class PermitAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permit_id = db.Column(db.Integer, db.ForeignKey('permit.id'))
    filename = db.Column(db.String(255))
    file_type = db.Column(db.String(20))  # pdf, jpg, dwg
    file_path = db.Column(db.String(255))

    permit = db.relationship('Permit', backref='attachments')

class PermitReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permit_id = db.Column(db.Integer, db.ForeignKey('permit.id'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # 'approved' or 'rejected'
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    permit = db.relationship('Permit', backref='reviews')
    inspector = db.relationship('User')
