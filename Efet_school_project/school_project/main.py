####################################################################
###############          Import packages         ###################
####################################################################
from flask import Blueprint, render_template, flash, g, request, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from school_project import create_app
from school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
from school_project.tools import get_all_payments, get_student_infos, get_all_grades, get_all_majors, get_all_students, get_user_messages, get_all_users, get_student_absence, get_grades_mean, get_all_subjects, get_all_teachers, get_all_teachers, get_all_absence, get_one_payment
import sqlite3
from school_project import db
from datetime import datetime
from fpdf import FPDF
from pathlib import Path
from functools import wraps
import os

def require_approved_user(f):
    """Decorator to require that user has been approved by admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.role == 'visiteur' or current_user.status == 'pending':
                flash('Votre compte est en attente d\'approbation. L\'administration vous contactera dans les 72 heures pour confirmer votre situation.', 'warning')
                return render_template('pending_approval.html')
        return f(*args, **kwargs)
    return decorated_function

####################################################################
# our main blueprint
main = Blueprint('main', __name__)

####################################################################
@main.route('/forbidden') # home page
def forbidden():
    return render_template('forbidden.html')

####################################################################
@main.route('/') # home page
def index():
    return render_template('index.html')

@main.route('/health') # health check for Railway
def health():
    """Health check endpoint for Railway deployment"""
    return {'status': 'healthy', 'service': 'EFET School Management System'}, 200

@main.route('/about_us') # about us page
def about_us():
    return render_template('about_us.html')

@main.route('/poles/commerce') # Pôle Commerce page
def pole_commerce():
    return render_template('pole_commerce.html')

@main.route('/poles/sante') # Pôle Santé page
def pole_sante():
    return render_template('pole_sante.html')

@main.route('/poles/finance') # Pôle Finance page
def pole_finance():
    return render_template('pole_finance.html')

@main.route('/poles/informatique') # Pôle Informatique page
def pole_informatique():
    return render_template('pole_informatique.html')

@main.route('/poles/logistique') # Pôle Logistique page
def pole_logistique():
    return render_template('pole_logistique.html')

@main.route('/poles/management') # Pôle Management page
def pole_management():
    return render_template('pole_management.html')

@main.route('/test') # home page
def test():
    return render_template('test.html')

####################################################################
@main.route('/sendMessage', methods = ['GET', 'POST'])
@login_required
@require_approved_user
def sendMessage():
    sender_id = current_user.id
    recipient_id = request.form.get('recipient_id')
    message_content = request.form.get('message')
    priority = request.form.get('priority', 'normal')  # Get priority, default to normal
    date_sent = datetime.now()

    # Validate inputs
    if not recipient_id or not message_content:
        flash('Destinataire et message sont requis.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Validate priority
    valid_priorities = ['normal', 'important', 'urgent']
    if priority not in valid_priorities:
        priority = 'normal'

    try:
        # Create message with backward compatibility
        message = Message(
            msg_from=sender_id, 
            msg_to=recipient_id, 
            content=message_content, 
            date_sent=date_sent
        )
        
        # Set priority and is_read if the model supports it
        if hasattr(message, 'priority'):
            message.priority = priority
        if hasattr(message, 'is_read'):
            message.is_read = False
        
        db.session.add(message)
        db.session.commit()
        flash('Message envoyé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de l\'envoi du message.', 'error')
        print(f"Error sending message: {e}")
    
    return redirect(url_for('main.dashboard'))

@main.route('/markMessageRead', methods=['POST'])
@login_required
@require_approved_user
def markMessageRead():
    message_id = request.form.get('message_id')
    
    if not message_id:
        return jsonify({'success': False, 'message': 'Message ID required'}), 400
    
    try:
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'message': 'Message not found'}), 404
        
        # Only allow the recipient to mark as read
        if message.msg_to != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        message.is_read = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Message marked as read'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating message'}), 500

####################################################################
@main.route('/profile') # profile page that return 'profile'
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/updateProfile', methods=['GET', 'POST']) # profile page that return 'profile'
@login_required
def updateProfile():
    user_id = current_user.id
    email = request.form.get('email')
    phone = request.form.get('phone')
    name = request.form.get('name')
    age = request.form.get('age')
    address = request.form.get('address')
    registration = request.form.get('registration')
    gender = request.form.get('gender')
    about_me = request.form.get('about_me')
    major = request.form.get('major')
    register_date = request.form.get('register_date')
    year = request.form.get('year')

    register_date_obj = datetime.strptime(register_date, '%Y-%m-%d')

    user = User.query.filter_by(id=user_id).first()
    user.email = email
    user.phone = phone
    user.name = name
    user.age = age
    user.address = address
    user.registration = registration
    user.gender = gender
    user.about_me = about_me
    user.major = major
    user.register_date = register_date_obj
    user.year = year

    db.session.commit()
    return redirect(url_for('main.profile'))

@main.route('/uploadPicture', methods = ['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f:
            # Ensure upload directory exists
            upload_dir = os.path.join(current_app.static_folder, 'uploaded_pictures')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            filename = f.filename
            file_path = os.path.join(upload_dir, filename)
            f.save(file_path)
            
            # Store relative path in database
            relative_path = f'/static/uploaded_pictures/{filename}'
            user = User.query.filter_by(id=current_user.id).first()
            user.profile_picture = relative_path
            db.session.commit()
        return redirect(url_for('main.profile'))

####################################################################

@main.route('/dashboard')
@login_required
@require_approved_user
def dashboard():
    messages = get_user_messages(current_user.id)
    # if you are an admin: go to admin dashboard (manage students, grades, payments, majors ..)
    if current_user.role == 'admin':
        students = get_all_students()
        majors = get_all_majors()
        all_subject = get_all_subjects()
        all_teacher = get_all_teachers()
        # Get pending notifications for admin
        pending_notifications = AdminNotification.query.filter_by(is_read=False).order_by(AdminNotification.created_at.desc()).all()
        return render_template('dashboard.html', users=students, majors=majors, messages=messages, all_subject=all_subject, all_teacher=all_teacher, notifications=pending_notifications)
    elif current_user.role == 'teacher':
        all_users = get_all_users()
        students = get_all_students()
        majors = get_all_majors()
        all_absence = get_all_absence()
        student_infos = get_student_infos(current_user.id)
        return render_template('dashboard_teacher.html', student_infos=student_infos, messages=messages, students=students, absences=all_absence, users=all_users, majors=majors)
    # if you are a student: go to student dashboard (see grades, messages, ..)
    elif current_user.role == 'student':
        all_users = get_all_students()
        student_absence = get_student_absence(current_user.id)
        student_infos = get_student_infos(current_user.id)
        return render_template('dashboard_student.html', student_infos=student_infos, messages=messages, users=all_users, absences=student_absence)
    else:
        # Fallback for users with undefined roles
        flash('Role utilisateur non reconnu. Veuillez contacter l\'administrateur.', 'error')
        return redirect(url_for('main.index'))

####################################################################

@main.route('/consultAbsence/<user_id>')
@login_required
def consultAbsence(user_id):
    absence = get_student_absence(user_id)
    student_infos = get_student_infos(user_id)
    return render_template('absence.html', absences=absence, student_infos=student_infos)

@main.route('/addAbsence', methods=['GET', 'POST'])
@login_required
def addAbsence():
    if current_user.role == 'student':
        return redirect('/forbidden')
    if current_user.role == 'teacher':
        student_id = request.form.get('student_id')
        date_absence = request.form.get('date_absence')
        justified = request.form.get('justified')
        details = request.form.get('details')

        date_absence_obj = datetime.strptime(date_absence, '%Y-%m-%dT%H:%M')
        new_absence = Absence(student_id=student_id, date_absence=date_absence_obj, justified=justified, details=details)
        db.session.add(new_absence)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    else:
        user_id = request.form.get('user_id')
        date_absence = request.form.get('date_absence')
        justified = request.form.get('justified')
        details = request.form.get('details')

        date_absence_obj = datetime.strptime(date_absence, '%Y-%m-%dT%H:%M')
        new_absence = Absence(student_id=user_id, date_absence=date_absence_obj, justified=justified, details=details)
        db.session.add(new_absence)
        db.session.commit()
        return redirect(f'consultAbsence/{user_id}')

@main.route('/deleteAbsence', methods=['GET', 'POST'])
@login_required
def deleteAbsence():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = current_user.id
        absence_id = request.form.get('absence_id')

        grade = Absence.query.filter(Absence.id == absence_id).delete()
        db.session.commit()
        return redirect(f'consultAbsence/{user_id}')

@main.route('/editAbsence', methods=['GET', 'POST'])
@login_required
def editAbsence():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        absence_id = request.form.get('absence_id')
        date_absence = request.form.get('date_absence')
        justified = request.form.get('justified')
        details = request.form.get('details')

        date_absence_obj = datetime.strptime(date_absence, '%Y-%m-%dT%H:%M')

        absence_row = Absence.query.filter(Absence.id == absence_id).first()
        absence_row.justified = justified
        absence_row.date_absence = date_absence_obj
        absence_row.details = details

        db.session.commit()
        return redirect(f'consultAbsence/{user_id}')

####################################################################

@main.route('/consultGrades/<user_id>')
@login_required
def consultGrades(user_id):
    all_subject = get_all_subjects()
    all_grades = get_all_grades(user_id)
    student_infos = get_student_infos(user_id)
    return render_template('grades.html', all_grades=all_grades, student_infos=student_infos, all_subject=all_subject)

@main.route('/consultGradesStudent/<user_id>')
@login_required
def consultGradesStudent(user_id):
    if int(user_id) == current_user.id or current_user.role == 'admin':
        all_grades = get_all_grades(user_id)
        student_infos = get_student_infos(user_id)
        grades_mean = get_grades_mean(user_id)
        return render_template('grades_student.html', all_grades=all_grades, student_infos=student_infos, grades_mean=grades_mean)
    else:
        return redirect('/forbidden')

@main.route('/addGrade', methods=['GET', 'POST'])
@login_required
def addGrade():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        grade = request.form.get('grade')
        subject = request.form.get('subject')
        grade_date = request.form.get('grade_date')

        grade_date_obj = datetime.strptime(grade_date, '%Y-%m-%d')
        new_grade = Grade(student_id=user_id, grade=grade, subject=subject, grade_date=grade_date_obj)
        db.session.add(new_grade)
        db.session.commit()
        return redirect(f'consultGrades/{user_id}')

@main.route('/deleteGrade', methods=['GET', 'POST'])
@login_required
def deleteGrade():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        grade_id = request.form.get('grade_id')

        grade = Grade.query.filter(Grade.id == grade_id).delete()
        db.session.commit()
        return redirect(f'consultGrades/{user_id}')

@main.route('/editGrade', methods=['GET', 'POST'])
@login_required
def editGrade():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        grade_id = request.form.get('grade_id')
        grade = request.form.get('grade')
        grade_date = request.form.get('grade_date')
        subject = request.form.get('subject')

        grade_date_obj = datetime.strptime(grade_date, '%Y-%m-%d')

        grade_row = Grade.query.filter(Grade.id == grade_id).first()
        grade_row.grade = grade
        grade_row.grade_date = grade_date_obj
        grade_row.subject = subject

        db.session.commit()
        return redirect(f'consultGrades/{user_id}')

####################################################################

@main.route('/addMajor', methods=['GET', 'POST'])
@login_required
def addMajor():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        major_name = request.form.get('major_name')
        duration = request.form.get('duration')

        if major_name != None and duration != None:
            new_major = Major(major_name=major_name, duration=duration)
            db.session.add(new_major)
            db.session.commit()
        return redirect('/dashboard')

@main.route('/deleteMajor', methods=['GET', 'POST'])
@login_required
def deleteMajor():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        major_id = request.form.get('major_id')
        major = Major.query.filter(Major.id == major_id).delete()
        db.session.commit()
        return redirect('/dashboard')

@main.route('/editMajor', methods=['GET', 'POST'])
@login_required
def editMajor():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        major_id = request.form.get('major_id')
        major_name = request.form.get('major_name')
        duration = request.form.get('duration')

        major_row = Major.query.filter(Major.id == major_id).first()
        major_row.major_name = major_name
        major_row.duration = duration

        db.session.commit()
        return redirect('/dashboard')

####################################################################

####################################################################

@main.route('/addSubject', methods=['GET', 'POST'])
@login_required
def addSubject():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        subject_name = request.form.get('subject_name')
        teacher_id = request.form.get('prof_id')

        print("===> ", teacher_id)

        if subject_name != None and subject_name != '':
            new_subject = Subject(name=subject_name, id_prof=teacher_id)
            db.session.add(new_subject)
            db.session.commit()
        return redirect('/dashboard')

@main.route('/deleteSubject', methods=['GET', 'POST'])
@login_required
def deleteSubject():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        subject_id = request.form.get('subject_id')
        subject = Subject.query.filter(Subject.id == subject_id).delete()
        db.session.commit()
        return redirect('/dashboard')

@main.route('/editSubject', methods=['GET', 'POST'])
@login_required
def editSubject():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        subject_id = request.form.get('subject_id')
        subject_name = request.form.get('subject_name')
        teacher_id = request.form.get('prof_id')

        subject_row = Subject.query.filter(Subject.id == subject_id).first()
        subject_row.name = subject_name
        subject_row.id_prof = teacher_id

        db.session.commit()
        return redirect('/dashboard')

####################################################################

@main.route('/consultPayments/<user_id>')
@login_required
def consultPayments(user_id):
    all_payments = get_all_payments(user_id)
    student_infos = get_student_infos(user_id)
    return render_template('payments.html', all_payments=all_payments, student_infos=student_infos)

@main.route('/addPayment', methods=['GET', 'POST'])
@login_required
def addPayment():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        month_paid = request.form.get('month_paid')
        payment_date = request.form.get('payment_date')
        amount = request.form.get('amount')
        status = request.form.get('status')
        type = request.form.get('type')

        month_paid_obj = datetime.strptime(month_paid, "%Y-%m")
        payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d")
        new_payment = Payment(student_id=user_id, month_paid=month_paid_obj, payment_date=payment_date_obj, amount=amount, status=status, type=type)
        db.session.add(new_payment)
        db.session.commit()

        return redirect(f'consultPayments/{user_id}')
        #return render_template('payments.html', all_payments=all_payments)

@main.route('/deletePayment', methods=['GET', 'POST'])
@login_required
def deletePayment():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        payment_id = request.form.get('payment_id')

        payment = Payment.query.filter(Payment.id == payment_id).delete()
        db.session.commit()

        return redirect(f'consultPayments/{user_id}')

@main.route('/editPayment', methods=['GET', 'POST'])
@login_required
def editPayment():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        payment_id = request.form.get('payment_id')
        month_paid = request.form.get('month_paid')
        payment_date = request.form.get('payment_date')
        amount = request.form.get('amount')
        status = request.form.get('status')
        type = request.form.get('type')

        month_paid_obj = datetime.strptime(month_paid, "%Y-%m")
        payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d")

        payment = Payment.query.filter(Payment.id == payment_id).first()
        payment.month_paid = month_paid_obj
        payment.payment_date = payment_date_obj
        payment.amount = amount
        payment.status = status
        payment.type = type

        db.session.commit()
        return redirect(f'consultPayments/{user_id}')

@main.route('/generatePdfPayment/<user_id>/<payment_id>', methods=['GET', 'POST'])
@login_required
def generate_pdf_payment(user_id, payment_id):
    payment = get_one_payment(payment_id)
    student_infos = get_student_infos(user_id)

    pdf = FPDF()

    pdf.add_page()
    pdf.set_font("Arial", size = 15)

    pdf.image('logo_ecole.png', x = None, y = None, w = 0, h = 0, type = '', link = 'logo_ecole.png')

    pdf.cell(200, 10, txt = "**** Payment proof ****", ln = 1, align = 'C')

    pdf.cell(200, 10, txt = f"- Student Id : {user_id}", ln = 2, align = 'C')
    pdf.cell(200, 10, txt = f"- Student Name : {student_infos.name}", ln = 3, align = 'C')
    pdf.cell(200, 10, txt = f"- Student Year : {student_infos.year}", ln = 4, align = 'C')
    pdf.cell(200, 10, txt = f"- Student Registration : {student_infos.registration}", ln = 5, align = 'C')

    pdf.cell(200, 10, txt = "---------------------------------", ln = 6, align = 'C')

    pdf.cell(200, 10, txt = f"Payment Date : {payment.payment_date}", ln = 7, align = 'C')
    pdf.cell(200, 10, txt = f"Payment Amount : {payment.amount}", ln = 8, align = 'C')
    pdf.cell(200, 10, txt = f"Payment Status : {payment.status}", ln = 9, align = 'C')
    pdf.cell(200, 10, txt = f"Payment Type : {payment.type}", ln = 10, align = 'C')

    pdf.output(f"payment_student_{user_id}.pdf")
    return redirect(url_for('main.dashboard'))

####################################################################

@main.route('/addStudent', methods=['GET', 'POST'])
@login_required
def addStudent():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        age = request.form.get('age')
        address = request.form.get('address')
        registration = request.form.get('registration')
        register_date = request.form.get('register_date')
        major = request.form.get('major')
        gender = request.form.get('gender')
        role = request.form.get('role')
        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to
            flash('Email address already exists')
            results = get_all_students()
            return render_template('dashboard.html', users=results)
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role, age=age, address=address, registration=registration, gender=gender)
        db.session.add(new_user)
        db.session.commit()

        results = get_all_students()
        return redirect(url_for('main.dashboard'))
        #return render_template('dashboard.html', users=results)

@main.route('/deleteStudent', methods=['GET', 'POST'])
@login_required
def deleteStudent():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        # delete the selected user
        # delete from user where id = ??
        user_id = request.form.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

@main.route('/editStudent', methods=['GET', 'POST'])
@login_required
def editStudent():
    if current_user.role == 'student':
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        age = request.form.get('age')
        address = request.form.get('address')
        registration = request.form.get('registration')
        gender = request.form.get('gender')
        major = request.form.get('major')
        current_year = request.form.get('current_year')
        register_date = request.form.get('register_date')
        role = request.form.get('role')

        user = User.query.filter_by(id=user_id).first()
        user.email = email
        user.name = name
        user.age = age
        user.address = address
        user.registration = registration
        user.gender = gender
        user.major = major
        user.year = current_year
        user.phone = phone
        user.role = role

        if register_date != None and register_date != '':
            register_date_obj = datetime.strptime(register_date, "%Y-%m-%d")
            user.register_date = register_date_obj

        if password != '' and password != None:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')

        db.session.commit()
        return redirect(url_for('main.dashboard'))
        # return render_template('dashboard.html', users=results)

@main.route('/editTeacher', methods=['GET', 'POST'])
@login_required
def editTeacher():
    if current_user.role not in ['admin', 'teacher']:
        return redirect('/forbidden')
    else:
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        address = request.form.get('address')
        speciality = request.form.get('speciality')
        role = request.form.get('role')
        
        # Fields for student conversion
        registration = request.form.get('registration')
        major = request.form.get('major')
        current_year = request.form.get('current_year')
        
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.email = email
            user.name = name
            user.address = address
            user.phone = phone
            
            # Update role and related fields
            if role:
                user.role = role
                
                # If converting to student, update student-specific fields
                if role == 'student':
                    user.registration = registration
                    user.major = major
                    user.year = current_year
                
            if password and password.strip():
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                
            db.session.commit()
            
            if role == 'student':
                flash('Enseignant converti en étudiant avec succès', 'success')
            else:
                flash('Enseignant mis à jour avec succès', 'success')
        
        return redirect(url_for('main.dashboard'))

@main.route('/get_student_data/<int:student_id>', methods=['GET'])
@login_required
def get_student_data(student_id):
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    student = User.query.get(student_id)
    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404
    
    # Convert student to JSON-friendly format
    student_data = {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "age": student.age,
        "address": student.address,
        "registration": student.registration,
        "gender": student.gender,
        "role": student.role,
        "major": student.major,
        "year": student.year,
        "phone": student.phone,
        "register_date": student.register_date.strftime('%Y-%m-%d') if student.register_date else None
    }
    
    return jsonify({"success": True, "student": student_data})

# Admin routes for user management
@main.route('/admin/notifications')
@login_required
def admin_notifications():
    if current_user.role != 'admin':
        return redirect('/forbidden')
    
    # Get all notifications with user information
    notifications = AdminNotification.query.order_by(AdminNotification.created_at.desc()).all()
    
    # Fetch users for each notification and attach them to the notification objects
    for notification in notifications:
        user = User.query.get(notification.user_id)
        # Only set the user if it exists
        if user:
            notification.user = user
    
    return render_template('admin_notifications.html', notifications=notifications)

@main.route('/admin/approve_user', methods=['POST'])
@login_required
def approve_user():
    if current_user.role != 'admin':
        return redirect('/forbidden')
    
    user_id = request.form.get('user_id')
    new_role = request.form.get('role')  # student or teacher
    
    user = User.query.get(user_id)
    if user:
        user.role = new_role
        user.status = 'approved'
        
        # Mark notification as resolved
        notification = AdminNotification.query.filter_by(user_id=user_id, is_read=False).first()
        if notification:
            notification.is_read = True
            notification.resolved_at = datetime.now()
            notification.resolved_by = current_user.id
        
        db.session.commit()
        flash(f'Utilisateur {user.name} approuvé avec le rôle {new_role}', 'success')
    
    return redirect(url_for('main.admin_notifications'))

@main.route('/admin/reject_user', methods=['POST'])
@login_required
def reject_user():
    if current_user.role != 'admin':
        return redirect('/forbidden')
    
    user_id = request.form.get('user_id')
    
    user = User.query.get(user_id)
    if user:
        user.status = 'rejected'
        
        # Mark notification as resolved
        notification = AdminNotification.query.filter_by(user_id=user_id, is_read=False).first()
        if notification:
            notification.is_read = True
            notification.resolved_at = datetime.now()
            notification.resolved_by = current_user.id
        
        db.session.commit()
        flash(f'Utilisateur {user.name} rejeté', 'warning')
    
    return redirect(url_for('main.admin_notifications'))

@main.route('/admin/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
    if current_user.role != 'admin':
        return redirect('/forbidden')
    
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        user = User.query.get(user_id) if user_id else None
        return render_template('send_email.html', user=user)
    
    else:
        recipient_id = request.form.get('recipient_id')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Log the email (in a real application, you would send an actual email)
        email_log = EmailLog(
            recipient_id=recipient_id,
            sender_id=current_user.id,
            subject=subject,
            message=message,
            status='sent'
        )
        db.session.add(email_log)
        db.session.commit()
        
        flash('Email envoyé avec succès', 'success')
        return redirect(url_for('main.admin_notifications'))

@main.route('/admin/pending_users')
@login_required
def pending_users():
    if current_user.role != 'admin':
        return redirect('/forbidden')
    
    pending_users = User.query.filter_by(status='pending').all()
    return render_template('pending_users.html', users=pending_users)

####################################################################
app = create_app() # we initialize our flask app using the
####################################################################

if __name__ == '__main__':
    app.run(debug=True) # run the flask app on debug mode

