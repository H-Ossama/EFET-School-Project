#!/usr/bin/env python3
"""
Database Migration Script for Railway Deployment
This script initializes the PostgreSQL database with all required tables
"""

import os
import sys

# Add the application paths
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'Efet_school_project')
school_project_dir = os.path.join(app_dir, 'school_project')

# Add paths to Python path
sys.path.insert(0, current_dir)
sys.path.insert(0, app_dir)
sys.path.insert(0, school_project_dir)

try:
    from Efet_school_project.school_project import create_app, db
    from Efet_school_project.school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
    from werkzeug.security import generate_password_hash
    from datetime import datetime
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import paths...")
    try:
        os.chdir(app_dir)  # Change to app directory
        from school_project import create_app, db
        from school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
        from werkzeug.security import generate_password_hash
        from datetime import datetime
    except ImportError as e2:
        print(f"Secondary import error: {e2}")
        sys.exit(1)

def create_admin_user():
    """Create a default admin user if none exists"""
    # Create custom admin account
    custom_admin = User.query.filter_by(email='ossamahattan@gmail.com').first()
    if not custom_admin:
        custom_admin_user = User(
            email='ossamahattan@gmail.com',
            name='Ossama Hattan',
            password=generate_password_hash('1324Haddadi@', method='pbkdf2:sha256'),
            role='admin',
            status='approved',
            age=30,
            address='EFET School',
            registration='ADMIN001',
            gender='Male',
            register_date=datetime.now().date()
        )
        db.session.add(custom_admin_user)
        db.session.commit()
        print("✅ Custom admin user created successfully!")
        print("   Email: ossamahattan@gmail.com")
    else:
        # Ensure the user has admin role
        if custom_admin.role != 'admin':
            custom_admin.role = 'admin'
            custom_admin.status = 'approved'
            db.session.commit()
            print("✅ Updated existing user to admin role")
        else:
            print("✅ Custom admin user already exists")
    
    # Also create default admin as backup
    admin = User.query.filter_by(email='admin@efet.edu').first()
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
        print("✅ Default admin user created successfully!")
        print("   Email: admin@efet.edu")
        print("   Password: admin123")
        print("   ⚠️  Please change the password after first login!")
    else:
        print("✅ Default admin user already exists")

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