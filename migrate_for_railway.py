#!/usr/bin/env python3
"""
Database Migration Script for Railway Deployment
This script initializes the PostgreSQL database with all required tables
"""

import os
import sys

# Add the school_project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Efet_school_project', 'school_project'))

from school_project import create_app, db
from school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Create a default admin user if none exists"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            email='admin@efet.edu',
            name='Administrator',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin',
            status='approved',
            age=30,
            address='EFET School',
            registration='ADMIN001',
            gender='Other',
            register_date=datetime.now().date()
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully!")
        print("   Email: admin@efet.edu")
        print("   Password: admin123")
        print("   ⚠️  Please change the password after first login!")
    else:
        print("✅ Admin user already exists")

def create_sample_majors():
    """Create sample majors if none exist"""
    if Major.query.count() == 0:
        majors = [
            Major(major_name='Informatique', duration=3.0),
            Major(major_name='Commerce', duration=2.0),
            Major(major_name='Finance', duration=2.5),
            Major(major_name='Santé', duration=3.0),
            Major(major_name='Logistique', duration=2.0),
            Major(major_name='Management', duration=2.5)
        ]
        for major in majors:
            db.session.add(major)
        db.session.commit()
        print("✅ Sample majors created successfully!")
    else:
        print("✅ Majors already exist")

def main():
    """Main migration function"""
    print("🚀 Starting database migration for Railway deployment...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create admin user
            print("👤 Setting up admin user...")
            create_admin_user()
            
            # Create sample majors
            print("📚 Setting up sample majors...")
            create_sample_majors()
            
            print("\n🎉 Database migration completed successfully!")
            print("🌐 Your application is ready for Railway deployment!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()