#!/usr/bin/env python3
"""Test authentication and API endpoints"""

import json
import urllib.request
import urllib.parse

def test_login():
    """Test login endpoint"""
    print("=" * 60)
    print("Testing Login Endpoint")
    print("=" * 60)

    url = 'http://localhost:5000/api/auth/login'
    data = {
        'username': 'admin',
        'password': 'admin123'
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n[OK] Login successful!")
            print(f"  User: {result['user']['username']}")
            print(f"  Role: {result['user']['role']}")
            print(f"  Token: {result['token'][:50]}...")
            return result['token']
    except Exception as e:
        print(f"\n[FAIL] Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint with JWT"""
    print("\n" + "=" * 60)
    print("Testing Protected Endpoint (/api/pending-posts)")
    print("=" * 60)

    url = 'http://localhost:5000/api/pending-posts'

    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n[OK] Access granted!")
            print(f"  Pending posts count: {len(result.get('data', []))}")
            return True
    except urllib.error.HTTPError as e:
        print(f"\n[FAIL] Access denied: {e.code} - {e.reason}")
        return False

def test_public_endpoint():
    """Test public endpoint (no auth)"""
    print("\n" + "=" * 60)
    print("Testing Public Endpoint (/api/posts)")
    print("=" * 60)

    url = 'http://localhost:5000/api/posts'

    try:
        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\n[OK] Public access successful!")
            print(f"  Published posts count: {len(result.get('data', []))}")
            return True
    except Exception as e:
        print(f"\n[FAIL] Failed: {e}")
        return False

def test_spa_serving():
    """Test SPA serving"""
    print("\n" + "=" * 60)
    print("Testing SPA Frontend (/ endpoint)")
    print("=" * 60)

    url = 'http://localhost:5000/'

    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            if '<div id="app"></div>' in html:
                print(f"\n[OK] SPA shell loaded successfully!")
                print(f"  Contains: <div id='app'></div>")
                return True
            else:
                print(f"\n[FAIL] SPA shell not found in response")
                return False
    except Exception as e:
        print(f"\n[FAIL] Failed: {e}")
        return False

if __name__ == '__main__':
    print("\nTesting Authentication System\n")

    # Test 1: Login
    token = test_login()

    if token:
        # Test 2: Protected endpoint with JWT
        test_protected_endpoint(token)

    # Test 3: Public endpoint
    test_public_endpoint()

    # Test 4: SPA serving
    test_spa_serving()

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60 + "\n")
