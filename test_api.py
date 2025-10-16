#!/usr/bin/env python3
"""Test script to verify API functionality"""

import requests
import json
import time

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:8005"
    
    print("Testing PTCC API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test search endpoint
    try:
        response = requests.get(f"{base_url}/api/search/?q=student", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search API: Found {len(results)} results")
            if results:
                print(f"   Top result: {results[0].get('title', 'N/A')}")
        else:
            print(f"❌ Search API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search API error: {e}")
        return False
    
    # Test students endpoint
    try:
        response = requests.get(f"{base_url}/api/students/", timeout=5)
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Students API: Found {len(students)} students")
        else:
            print(f"❌ Students API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Students API error: {e}")
    
    # Test briefing endpoint
    try:
        response = requests.get(f"{base_url}/api/briefing/", timeout=5)
        if response.status_code == 200:
            briefing = response.json()
            print(f"✅ Briefing API: Generated for {briefing.get('date', 'N/A')}")
        else:
            print(f"❌ Briefing API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Briefing API error: {e}")
    
    print("\n🎉 API testing completed!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to start
    time.sleep(2)
    test_api()