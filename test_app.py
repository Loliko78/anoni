#!/usr/bin/env python3
"""
Тестирование приложения
"""

import sys
import os

def test_imports():
    """Test imports"""
    try:
        from app import app, db
        print("+ Imports successful")
        return True
    except Exception as e:
        print(f"- Import error: {e}")
        return False

def test_database():
    """Test database"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("+ Database created")
            return True
    except Exception as e:
        print(f"- Database error: {e}")
        return False

def test_routes():
    """Test routes"""
    try:
        from app import app
        with app.test_client() as client:
            # Test main page (should redirect to login)
            response = client.get('/')
            print(f"+ Main page: {response.status_code}")
            
            # Test login page
            response = client.get('/login')
            print(f"+ Login page: {response.status_code}")
            
            return True
    except Exception as e:
        print(f"- Routes error: {e}")
        return False

def main():
    print("Testing Harvest Messenger")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_database()
    success &= test_routes()
    
    print("=" * 40)
    if success:
        print("All tests passed!")
        print("App ready to run: python app.py")
    else:
        print("There are errors!")
    
    return success

if __name__ == '__main__':
    main()