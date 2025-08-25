#!/usr/bin/env python3
"""
Test browser-like access to identify 500 errors
"""

import requests

def test_browser_access():
    """Test with browser-like headers"""
    print("Testing browser-like access...")
    print("=" * 40)
    
    # Browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Test routes
    routes = [
        '/',
        '/login',
        '/chats',
        '/profile',
        '/admin',
        '/search'
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    
    for route in routes:
        try:
            print(f"Testing {route}...")
            response = session.get(f'http://localhost:5000{route}', timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"  ✗ 500 ERROR on {route}!")
                print(f"  Response: {response.text[:500]}...")
            elif response.status_code == 200:
                print(f"  ✓ {route} OK")
            elif response.status_code == 302:
                print(f"  → {route} Redirect")
            else:
                print(f"  ⚠ {route} Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error accessing {route}: {e}")
    
    # Test login POST
    print("\nTesting login POST...")
    try:
        login_data = {
            'username': 'azazel',
            'password': 'Log1progress',
            'submit': 'Войти'
        }
        response = session.post('http://localhost:5000/login', data=login_data, timeout=10)
        print(f"Login POST status: {response.status_code}")
        
        if response.status_code == 500:
            print("✗ 500 ERROR during login!")
            print(f"Response: {response.text[:500]}...")
        elif response.status_code in [200, 302]:
            print("✓ Login successful")
            
            # Test protected routes after login
            print("\nTesting protected routes after login...")
            protected_routes = ['/chats', '/profile', '/admin']
            for route in protected_routes:
                try:
                    response = session.get(f'http://localhost:5000{route}', timeout=10)
                    print(f"  {route}: {response.status_code}")
                    
                    if response.status_code == 500:
                        print(f"  ✗ 500 ERROR on {route} after login!")
                        print(f"  Response: {response.text[:300]}...")
                    elif response.status_code == 200:
                        print(f"  ✓ {route} OK after login")
                    else:
                        print(f"  ⚠ {route} Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ✗ Error accessing {route}: {e}")
        else:
            print(f"⚠ Unexpected login status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during login POST: {e}")

if __name__ == "__main__":
    test_browser_access() 