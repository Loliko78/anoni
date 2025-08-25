#!/usr/bin/env python3
"""
Debug version to test login function
"""

from app import app, db
from models import User
from werkzeug.security import check_password_hash
from flask_login import login_user

def debug_login():
    """Debug login function"""
    print("Debugging login function...")
    
    with app.app_context():
        try:
            # Test 1: Check if user exists
            print("1. Checking if user 'azazel' exists...")
            user = User.query.filter_by(nickname_enc='azazel').first()
            if user:
                print(f"✓ User found: ID={user.id}, banned={user.banned}, is_admin={user.is_admin}")
            else:
                print("✗ User 'azazel' not found!")
                return
            
            # Test 2: Check password
            print("2. Checking password...")
            password = 'Log1progress'
            if check_password_hash(user.password_hash, password):
                print("✓ Password is correct")
            else:
                print("✗ Password is incorrect!")
                return
            
            # Test 3: Check if user is banned
            print("3. Checking if user is banned...")
            if user.banned:
                print("✗ User is banned!")
                return
            else:
                print("✓ User is not banned")
            
            # Test 4: Try to login user
            print("4. Attempting to login user...")
            try:
                result = login_user(user)
                print(f"✓ Login successful: {result}")
            except Exception as e:
                print(f"✗ Error during login_user: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 5: Check database connection
            print("5. Testing database connection...")
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✓ Database connection OK")
            except Exception as e:
                print(f"✗ Database error: {e}")
                
        except Exception as e:
            print(f"✗ General error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_login() 