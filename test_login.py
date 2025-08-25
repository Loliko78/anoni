#!/usr/bin/env python3
"""
Test login functionality and identify 500 errors
"""

import requests
from app import app

def test_login():
    """Test login functionality"""
    print("Testing login functionality...")
    print("=" * 40)
    
    # Test login page
    try:
        response = requests.get('http://localhost:5000/login', timeout=5)
        print(f"Login page status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"✗ Login page returned {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing login page: {e}")
        return
    
    # Test login POST request
    try:
        login_data = {
            'username': 'azazel',
            'password': 'Log1progress',
            'submit': 'Войти'
        }
        response = requests.post('http://localhost:5000/login', data=login_data, timeout=5)
        print(f"Login POST status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login POST successful")
            if "error" in response.text.lower() or "неверный" in response.text.lower():
                print("⚠ Login failed (wrong credentials)")
            else:
                print("✓ Login appears successful")
        elif response.status_code == 302:
            print("✓ Login successful (redirect)")
        elif response.status_code == 500:
            print("✗ 500 error during login!")
            print(f"Error response: {response.text[:500]}...")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during login POST: {e}")

def test_protected_routes():
    """Test protected routes after login"""
    print("\nTesting protected routes...")
    print("=" * 40)
    
    # Create session
    session = requests.Session()
    
    # Login first
    try:
        login_data = {
            'username': 'azazel',
            'password': 'Log1progress',
            'submit': 'Войти'
        }
        response = session.post('http://localhost:5000/login', data=login_data, timeout=5)
        
        if response.status_code in [200, 302]:
            print("✓ Login successful, testing protected routes...")
            
            # Test protected routes
            routes = ['/chats', '/profile', '/admin']
            for route in routes:
                try:
                    response = session.get(f'http://localhost:5000{route}', timeout=5)
                    print(f"{route}: {response.status_code}")
                    
                    if response.status_code == 500:
                        print(f"✗ 500 error on {route}!")
                        print(f"Error response: {response.text[:300]}...")
                    elif response.status_code == 200:
                        print(f"✓ {route} accessible")
                    else:
                        print(f"⚠ {route} returned {response.status_code}")
                        
                except Exception as e:
                    print(f"✗ Error accessing {route}: {e}")
        else:
            print(f"✗ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during login: {e}")

if __name__ == "__main__":
    test_login()
    test_protected_routes() 