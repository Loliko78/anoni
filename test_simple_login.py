#!/usr/bin/env python3
"""
Simple test to identify 500 error cause
"""

import requests

def test_simple_login():
    """Test simple login to identify 500 error"""
    print("Testing simple login...")
    
    # Test 1: GET login page
    try:
        response = requests.get('http://localhost:5000/login', timeout=5)
        print(f"GET login page: {response.status_code}")
        if response.status_code == 500:
            print("✗ 500 ERROR on GET login page!")
            print(f"Response: {response.text[:500]}...")
        else:
            print("✓ GET login page OK")
    except Exception as e:
        print(f"✗ Error on GET login: {e}")
    
    # Test 2: POST login with correct credentials
    try:
        data = {
            'nickname': 'azazel',
            'password': 'Log1progress'
        }
        response = requests.post('http://localhost:5000/login', data=data, timeout=5)
        print(f"POST login: {response.status_code}")
        
        if response.status_code == 500:
            print("✗ 500 ERROR on POST login!")
            print(f"Response: {response.text[:500]}...")
        elif response.status_code == 302:
            print("✓ Login successful (redirect)")
        elif response.status_code == 200:
            print("✓ Login page returned (may be successful)")
        else:
            print(f"⚠ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error on POST login: {e}")
    
    # Test 3: POST login with wrong credentials
    try:
        data = {
            'nickname': 'wrong',
            'password': 'wrong'
        }
        response = requests.post('http://localhost:5000/login', data=data, timeout=5)
        print(f"POST wrong credentials: {response.status_code}")
        
        if response.status_code == 500:
            print("✗ 500 ERROR with wrong credentials!")
            print(f"Response: {response.text[:500]}...")
        else:
            print("✓ Wrong credentials handled correctly")
            
    except Exception as e:
        print(f"✗ Error with wrong credentials: {e}")

if __name__ == "__main__":
    test_simple_login() 