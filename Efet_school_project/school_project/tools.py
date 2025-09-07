from flask import Blueprint, render_template, flash, g, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from school_project import create_app
from school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
import sqlite3
from school_project import db


def connect_db():
    import os
    # Use absolute path for better reliability
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'instance', 'db.sqlite')
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    #Check if DB is there
    if not hasattr(g, 'sqlite3'):
        g.sqlite3_db = connect_db()
    return g.sqlite3_db

def get_all_payments(student_id):
    db = get_db()
    #create table payment(id integer primary key autoincrement, student_id integer, month_paid date, payment_date date, amount float, status text)
    cursor = db.execute(f"select p.id, p.student_id, p.month_paid, p.payment_date, p.amount, p.status, p.type, u.name from payment p INNER JOIN user u ON p.student_id=u.id where p.student_id = {student_id}")
    results = cursor.fetchall()
    return results

def get_student_infos(student_id):
    user = User.query.filter_by(id=student_id).first()
    return user

def get_all_users():
    users = User.query.all()
    return users

def get_all_students():
    users = User.query.filter_by(role='student').all()
    return users

def get_all_grades(student_id):
    # this function retrieves student's grades from table Grade
    grades = Grade.query.filter_by(student_id=student_id).all()
    return grades

def get_all_majors():
    db = get_db()
    cursor = db.execute(f"SELECT major.id, major.major_name AS major_name, duration, COUNT(user.id) AS number_students FROM major LEFT JOIN user ON major.major_name = user.major GROUP BY major.major_name ORDER BY number_students desc;")
    majors = cursor.fetchall()
    return majors

def get_user_messages(student_id):
    db = get_db()
    
    # Check if new columns exist in the message table
    cursor = db.execute("PRAGMA table_info(message)")
    columns = [col[1] for col in cursor.fetchall()]
    
    has_priority = 'priority' in columns
    has_is_read = 'is_read' in columns
    
    # Build query based on available columns
    base_query = f"""
        SELECT m.id AS mid, 
               m.content AS content, 
               u1.name AS msg_from, 
               u2.name AS msg_to, 
               m.date_sent AS date_sent"""
    
    if has_priority:
        base_query += ",\n               m.priority AS priority"
    else:
        base_query += ",\n               'normal' AS priority"
    
    if has_is_read:
        base_query += ",\n               m.is_read AS is_read"
    else:
        base_query += ",\n               0 AS is_read"
    
    base_query += f""",
               u1.role AS sender_role,
               u2.role AS recipient_role
        FROM message m 
        JOIN user u1 ON m.msg_from = u1.id 
        JOIN user u2 ON m.msg_to = u2.id 
        WHERE u1.id = {student_id} OR u2.id = {student_id}
        ORDER BY m.date_sent DESC
    """
    
    cursor = db.execute(base_query)
    messages = cursor.fetchall()
    return messages

def get_student_absence(student_id):
    absence = Absence.query.filter_by(student_id=student_id).all()
    return absence

def get_grades_mean(student_id):
    db = get_db()
    cursor = db.execute(f"select sum(grade)/count(*) AS mean, subject from grade where student_id = {student_id} group by subject;")
    grades_mean = cursor.fetchall()
    return grades_mean

def get_all_subjects():
    db = get_db()
    cursor = db.execute(f"select subject.id as id, subject.name as name, user.name as teacher_name from subject join user on subject.id_prof = user.id;")
    subjects = cursor.fetchall()
    return subjects

def get_all_teachers():
    teacher = User.query.filter_by(role='teacher').all()
    return teacher

def get_all_absence():
    db = get_db()
    cursor = db.execute(f"select a.id as id, a.student_id as student_id, a.date_absence as date_absence, a.justified as justified, a.details as details, u.name as student_name from absence a join user u on u.id = a.student_id;")
    all_absence = cursor.fetchall()
    return all_absence

def get_one_payment(payment_id):
    payment = Payment.query.filter_by(id=payment_id).first()
    return payment

def get_pending_users():
    """Get all users with pending status"""
    users = User.query.filter_by(status='pending').all()
    return users

def get_admin_notifications():
    """Get all admin notifications"""
    notifications = AdminNotification.query.order_by(AdminNotification.created_at.desc()).all()
    return notifications

def get_unread_notifications_count():
    """Get count of unread admin notifications"""
    count = AdminNotification.query.filter_by(is_read=False).count()
    return count

def get_user_emails(user_id):
    """Get all emails sent to a user"""
    emails = EmailLog.query.filter_by(recipient_id=user_id).order_by(EmailLog.sent_at.desc()).all()
    return emails
