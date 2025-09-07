#!/usr/bin/env python3
"""
Test script to verify the Flask app can start locally
Run this before deploying to Railway
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    # Add current directory and school_project to path
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'school_project'))
    
    try:
        from school_project import create_app, db
        print("✅ Core imports successful")
        
        from school_project.models import User, Payment, Grade, Major
        print("✅ Models import successful")
        
        from school_project.main import main
        from school_project.auth import auth
        print("✅ Blueprints import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    print("\nTesting app creation...")
    
    try:
        from wsgi import app
        print("✅ App creation successful")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"Health response: {response.get_json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing EFET School Project Setup")
    print("=" * 50)
    
    # Change to the correct directory
    project_dir = Path(__file__).parent / 'Efet_school_project'
    if project_dir.exists():
        os.chdir(project_dir)
        print(f"📁 Changed to directory: {project_dir}")
    else:
        print(f"❌ Directory not found: {project_dir}")
        sys.exit(1)
    
    success = True
    success &= test_imports()
    success &= test_app_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your app is ready for Railway deployment.")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix Railway deployment'")
        print("3. git push")
        print("4. Deploy on Railway")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == '__main__':
    main()