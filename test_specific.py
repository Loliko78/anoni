#!/usr/bin/env python3
"""
Test specific scenarios that might cause 500 errors
"""

import requests
import time

def test_specific_scenarios():
    """Test specific scenarios that might cause 500 errors"""
    print("Testing specific scenarios...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test 1: Direct access to protected routes without login
    print("1. Testing protected routes without login...")
    protected_routes = ['/chats', '/profile', '/admin']
    for route in protected_routes:
        try:
            response = session.get(f'http://localhost:5000{route}', timeout=5)
            print(f"  {route}: {response.status_code}")
            if response.status_code == 500:
                print(f"  ✗ 500 ERROR on {route} without login!")
            elif response.status_code == 302:
                print(f"  → Redirect to login (expected)")
            else:
                print(f"  ⚠ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test 2: Login with wrong credentials
    print("\n2. Testing login with wrong credentials...")
    try:
        login_data = {
            'username': 'wrong_user',
            'password': 'wrong_password',
            'submit': 'Войти'
        }
        response = session.post('http://localhost:5000/login', data=login_data, timeout=5)
        print(f"  Wrong credentials login: {response.status_code}")
        if response.status_code == 500:
            print("  ✗ 500 ERROR with wrong credentials!")
        else:
            print("  ✓ Handled correctly")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 3: Login with correct credentials
    print("\n3. Testing login with correct credentials...")
    try:
        login_data = {
            'username': 'azazel',
            'password': 'Log1progress',
            'submit': 'Войти'
        }
        response = session.post('http://localhost:5000/login', data=login_data, timeout=5)
        print(f"  Correct credentials login: {response.status_code}")
        if response.status_code == 500:
            print("  ✗ 500 ERROR with correct credentials!")
            print(f"  Response: {response.text[:300]}...")
        else:
            print("  ✓ Login successful")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 4: Access protected routes after login
    print("\n4. Testing protected routes after login...")
    for route in protected_routes:
        try:
            response = session.get(f'http://localhost:5000{route}', timeout=5)
            print(f"  {route}: {response.status_code}")
            if response.status_code == 500:
                print(f"  ✗ 500 ERROR on {route} after login!")
                print(f"  Response: {response.text[:300]}...")
            elif response.status_code == 200:
                print(f"  ✓ {route} accessible")
            else:
                print(f"  ⚠ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test 5: Test logout
    print("\n5. Testing logout...")
    try:
        response = session.get('http://localhost:5000/logout', timeout=5)
        print(f"  Logout: {response.status_code}")
        if response.status_code == 500:
            print("  ✗ 500 ERROR during logout!")
        else:
            print("  ✓ Logout successful")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 6: Test non-existent routes
    print("\n6. Testing non-existent routes...")
    non_existent_routes = ['/nonexistent', '/admin/nonexistent', '/chats/999999']
    for route in non_existent_routes:
        try:
            response = session.get(f'http://localhost:5000{route}', timeout=5)
            print(f"  {route}: {response.status_code}")
            if response.status_code == 500:
                print(f"  ✗ 500 ERROR on non-existent route {route}!")
            elif response.status_code == 404:
                print(f"  ✓ 404 (expected)")
            else:
                print(f"  ⚠ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    test_specific_scenarios() 