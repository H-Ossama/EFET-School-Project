from flask_login import UserMixin
from __init__ import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.String(1000))
    status = db.Column(db.String(100), default='pending')  # pending, approved, rejected
    age = db.Column(db.Integer)
    address = db.Column(db.String(1000))
    registration = db.Column(db.String(1000))
    gender = db.Column(db.String(1000))
    profile_picture = db.Column(db.String(1000))
    about_me = db.Column(db.String(1000))
    phone = db.Column(db.String(100))
    major = db.Column(db.String(100))
    register_date = db.Column(db.Date)
    year = db.Column(db.Integer)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    student_id = db.Column(db.Integer)
    month_paid = db.Column(db.Date)
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Float)
    status = db.Column(db.String(1000))
    type = db.Column(db.String(1000))

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    grade = db.Column(db.Float)
    subject = db.Column(db.String(1000))
    grade_date = db.Column(db.Date)

class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100))
    duration = db.Column(db.Float)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg_from = db.Column(db.Integer)
    msg_to = db.Column(db.Integer)
    content = db.Column(db.String(1000))
    date_sent = db.Column(db.DateTime)  # Changed to DateTime for better precision
    priority = db.Column(db.String(20), default='normal')  # normal, important, urgent
    is_read = db.Column(db.Boolean, default=False)  # Track read status
    
    def __repr__(self):
        return f'<Message {self.id}: from {self.msg_from} to {self.msg_to}>'

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    date_absence = db.Column(db.DateTime)
    justified = db.Column(db.String(10))
    details = db.Column(db.String(1000))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    id_prof = db.Column(db.Integer)

class AdminNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), default='new_registration')  # new_registration, role_change, etc.
    message = db.Column(db.String(1000))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='sent')  # sent, failed, pending
    
    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_emails')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_emails')
