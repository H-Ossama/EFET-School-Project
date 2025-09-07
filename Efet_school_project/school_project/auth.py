####################################################################
##############          Import packages      #######################
####################################################################
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db


####################################################################
auth = Blueprint('auth', __name__) # create a Blueprint object that
                                   # we name 'auth'

####################################################################@auth.route('/logout') # define logout path
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['GET', 'POST'])# we define the sign up path
def signup(): # define the sign up function
    if request.method=='GET': # If the request is GET we return the
                              # sign up page and forms
        return render_template('signup.html')
    else: # if the request is POST, then we check if the email
          # doesn't already exist and then we save data
        try:
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')
            
            # Validate required fields
            if not email or not name or not password:
                flash('Tous les champs sont requis')
                return redirect(url_for('auth.signup'))
            
            user = User.query.filter_by(email=email).first() # if this
                                  # returns a user, then the email
                                  # already exists in database
            if user: # if a user is found, we want to redirect back to
                     # signup page so user can try again
                flash('Email address already exists')
                return redirect(url_for('auth.signup'))
            
            # Get additional fields with defaults
            from datetime import datetime
            
            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            new_user = User(
                email=email, 
                name=name,
                password=generate_password_hash(password, method='pbkdf2:sha256'), 
                role='visiteur', 
                status='pending',
                age=request.form.get('age', 18),
                address=request.form.get('address', ''),
                registration=f'USER_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                gender=request.form.get('gender', 'Other'),
                register_date=datetime.now().date()
            )
            
            #add the new user to the db
            db.session.add(new_user)
            db.session.commit()
            
            # Create an admin notification for new registration
            try:
                from models import AdminNotification
                notification = AdminNotification(
                    user_id=new_user.id,
                    notification_type='new_registration',
                    message=f"Nouvel utilisateur {new_user.name} ({new_user.email}) s'est inscrit et attend l'approbation."
                )
                db.session.add(notification)
                db.session.commit()
            except Exception as notif_error:
                # Don't fail signup if notification creation fails
                print(f"Notification creation failed: {notif_error}")
                db.session.rollback()
                db.session.commit()  # Commit the user anyway
            
            flash('Inscription réussie! Votre compte est en attente d\'approbation.')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.')
            print(f"Signup error: {e}")  # For debugging
            return redirect(url_for('auth.signup'))

@auth.route('/login', methods=['GET', 'POST']) # define login page path
def login(): # define login page function
    if request.method=='GET': # if the request is a GET we return the login page
        return render_template('login.html')
    else: # if the request is POST then we check if the user exist
          # and with the right password
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            # Validate required fields
            if not email or not password:
                flash('Email et mot de passe requis')
                return redirect(url_for('auth.login'))
            
            user = User.query.filter_by(email=email).first()
            
            # check if the user actually exists
            # take the user-supplied password, hash it, and compare it
            # to the hashed password in the database
            if not user:
                flash('Please sign up before!')
                return redirect(url_for('auth.signup'))
            elif not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('auth.login')) # if the user
                   #doesn't exist or password is wrong, reload the page
            
            # if the above check passes, then we know the user has the
            # right credentials
            login_user(user, remember=remember)
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            flash('Une erreur est survenue lors de la connexion. Veuillez réessayer.')
            print(f"Login error: {e}")  # For debugging
            return redirect(url_for('auth.login'))
