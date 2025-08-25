#!/usr/bin/env python3
"""
Test all routes to identify 500 errors
"""

import requests
import time
from app import app

def test_route(url, method='GET', data=None, expected_status=200):
    """Test a single route"""
    try:
        if method == 'GET':
            response = requests.get(f'http://localhost:5000{url}', timeout=5)
        elif method == 'POST':
            response = requests.post(f'http://localhost:5000{url}', data=data, timeout=5)
        
        status = response.status_code
        if status == expected_status:
            print(f"✓ {method} {url} - {status}")
            return True
        else:
            print(f"✗ {method} {url} - Expected {expected_status}, got {status}")
            if status == 500:
                print(f"   Error: {response.text[:200]}...")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {method} {url} - Connection refused (server not running)")
        return False
    except Exception as e:
        print(f"✗ {method} {url} - Exception: {e}")
        return False

def test_all_routes():
    """Test all routes systematically"""
    print("Testing all routes...")
    print("=" * 50)
    
    # Routes that should work without authentication (redirect to login)
    public_routes = [
        ('/', 'GET'),
        ('/login', 'GET'),
        ('/register', 'GET'),
        ('/search', 'GET'),  # This one works according to user
    ]
    
    # Routes that require authentication (should redirect to login)
    auth_routes = [
        ('/chats', 'GET'),
        ('/profile', 'GET'),
        ('/admin', 'GET'),
        ('/group/create', 'GET'),
        ('/channels/create', 'GET'),
    ]
    
    # Test public routes first
    print("\nTesting public routes:")
    for url, method in public_routes:
        test_route(url, method, expected_status=200)
    
    # Test auth routes (should redirect to login)
    print("\nTesting authenticated routes (should redirect to login):")
    for url, method in auth_routes:
        test_route(url, method, expected_status=302)  # Redirect to login
    
    # Test specific routes that might be causing issues
    print("\nTesting specific problematic routes:")
    specific_routes = [
        ('/chat/1', 'GET'),  # Should redirect to login
        ('/group/test123', 'GET'),  # Should redirect to login
        ('/channel/1', 'GET'),  # Should redirect to login
        ('/api/chats', 'GET'),  # Should redirect to login
    ]
    
    for url, method in specific_routes:
        test_route(url, method, expected_status=302)
    
    print("\n" + "=" * 50)
    print("Route testing completed!")

if __name__ == "__main__":
    test_all_routes() 