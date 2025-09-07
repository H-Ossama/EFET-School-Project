from flask import Flask
from school_project.models import User
from school_project import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite'
db.init_app(app)

with app.app_context():
    user = User.query.filter_by(email='ossamahattan@gmail.com').first()
    if user:
        print(f'User: {user.name}, Role: {user.role}, Status: {user.status}')
    else:
        print('User not found')