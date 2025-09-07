####################################################################
#################        Importing packages      ###################
####################################################################
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()

##################################################################### init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
####################################################################

def create_app():
    app = Flask(__name__) # creates the Flask instance, __name__ is
                          # the name of the current Python module
    
    # Configuration for both development and production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret-key-goes-here')
    
    # Database configuration - use PostgreSQL in production, SQLite in development
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Railway PostgreSQL - fix URL format if needed
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local SQLite - use absolute path
        instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        db_path = os.path.join(instance_path, 'db.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
                   # deactivate Flask-SQLAlchemy track modifications
    db.init_app(app) # Initialiaze sqlite database
    
    # The login manager contains the code that lets your application
    # and Flask-Login work together
    login_manager = LoginManager() # Create a Login Manager instance
    login_manager.login_view = 'auth.login' # define the redirection
                         # path when login required and we attempt
                         # to access without being logged in
    login_manager.init_app(app) # configure it for login
    
    # Import User model for login manager after db is initialized
    with app.app_context():
        from school_project.models import User
        
        @login_manager.user_loader
        def load_user(user_id): #reload user object from the user ID
                                #stored in the session
            # since the user_id is just the primary key of our user
            # table, use it in the query for the user
            return User.query.get(int(user_id))
    
    # blueprint for auth routes in our app
    # blueprint allow you to orgnize your flask app
    from school_project.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # blueprint for non-auth parts of app
    from school_project.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
