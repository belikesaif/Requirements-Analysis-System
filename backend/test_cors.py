#!/usr/bin/env python3

"""
Test CORS configuration for the backend API
"""

import requests
import json

def test_cors_configuration():
    """Test CORS headers and preflight requests"""
    
    # Backend URLs to test
    backend_urls = [
        "http://localhost:8000",  # Local development
        "https://requirements-analysis-system.onrender.com"  # Production
    ]
    
    # Frontend origins to test
    frontend_origins = [
        "https://nrasfrontend.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    for backend_url in backend_urls:
        print(f"\n🔍 Testing CORS for: {backend_url}")
        print("=" * 60)
        
        # Test health endpoint first
        try:
            response = requests.get(f"{backend_url}/health", timeout=10)
            print(f"✅ Health check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            continue
        
        # Test preflight requests
        for origin in frontend_origins:
            print(f"\n🌐 Testing origin: {origin}")
            
            # OPTIONS preflight request
            try:
                headers = {
                    'Origin': origin,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
                
                response = requests.options(
                    f"{backend_url}/api/process-requirements",
                    headers=headers,
                    timeout=10
                )
                
                print(f"   OPTIONS request: {response.status_code}")
                print(f"   CORS headers: {dict(response.headers)}")
                
                # Check specific CORS headers
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('access-control-allow-origin'),
                    'Access-Control-Allow-Methods': response.headers.get('access-control-allow-methods'),
                    'Access-Control-Allow-Headers': response.headers.get('access-control-allow-headers'),
                    'Access-Control-Allow-Credentials': response.headers.get('access-control-allow-credentials')
                }
                
                print("   CORS Analysis:")
                for key, value in cors_headers.items():
                    status = "✅" if value else "❌"
                    print(f"     {status} {key}: {value}")
                
            except Exception as e:
                print(f"   ❌ Preflight failed: {e}")
        
        # Test actual API endpoint
        print(f"\n📡 Testing API endpoint: {backend_url}/api/process-requirements")
        try:
            test_data = {
                "text": "The user logs into the system.",
                "title": "CORS Test Case Study"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'https://nrasfrontend.vercel.app'
            }
            
            response = requests.post(
                f"{backend_url}/api/process-requirements",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            print(f"   POST request: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("   ✅ API request successful")
                # Print first few keys of response
                try:
                    resp_data = response.json()
                    print(f"   📊 Response keys: {list(resp_data.keys())}")
                except:
                    pass
            else:
                print(f"   ❌ API request failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ API test failed: {e}")

if __name__ == "__main__":
    print("🧪 CORS Configuration Test")
    print("=" * 60)
    test_cors_configuration()
