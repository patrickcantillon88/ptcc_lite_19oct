#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTCC System Integration Test
Tests all components are working together correctly
"""

import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8005/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data['status']}")
            print(f"   Database: {data['database']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_students_api():
    """Test students API endpoint"""
    print("\n👥 Testing Students API...")
    try:
        response = requests.get("http://localhost:8005/api/students/", timeout=5)
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Students API working: {len(students)} students found")
            
            # Show sample students
            if students:
                sample = students[0]
                print(f"   Sample student: {sample['name']} ({sample['class_code']})")
                print(f"   Support level: {sample['support_level']}")
                if sample['support_notes']:
                    print(f"   Notes: {sample['support_notes']}")
            return True
        else:
            print(f"❌ Students API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Students API connection failed: {e}")
        return False

def test_briefing_api():
    """Test briefing API endpoint"""
    print("\n📋 Testing Briefing API...")
    try:
        response = requests.get("http://localhost:8005/api/briefing/today", timeout=5)
        if response.status_code == 200:
            briefing = response.json()
            print("✅ Briefing API working")
            print(f"   Date: {briefing.get('date', 'N/A')}")
            print(f"   Total students: {briefing.get('total_students', 'N/A')}")
            print(f"   Recent logs: {briefing.get('recent_logs_count', 'N/A')}")
            return True
        else:
            print(f"❌ Briefing API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Briefing API connection failed: {e}")
        return False

def test_mobile_pwa_proxy():
    """Test mobile PWA proxy to backend"""
    print("\n📱 Testing Mobile PWA Proxy...")
    try:
        response = requests.get("http://localhost:5173/api/students/", timeout=5)
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Mobile PWA proxy working: {len(students)} students found")
            return True
        else:
            print(f"❌ Mobile PWA proxy failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mobile PWA proxy connection failed: {e}")
        return False

def test_desktop_web_config():
    """Test desktop web configuration"""
    print("\n🖥️  Testing Desktop Web Configuration...")
    try:
        # Read the desktop web app config
        with open('frontend/desktop-web/app.py', 'r') as f:
            content = f.read()
            if 'API_BASE = "http://localhost:8005"' in content:
                print("✅ Desktop web configured for port 8005")
                return True
            else:
                print("❌ Desktop web not configured for port 8005")
                return False
    except Exception as e:
        print(f"❌ Desktop web config check failed: {e}")
        return False

def test_mobile_pwa_config():
    """Test mobile PWA configuration"""
    print("\n📱 Testing Mobile PWA Configuration...")
    try:
        # Read the mobile PWA config
        with open('frontend/mobile-pwa/vite.config.ts', 'r') as f:
            content = f.read()
            if 'target: \'http://localhost:8005\'' in content:
                print("✅ Mobile PWA configured for port 8005")
                return True
            else:
                print("❌ Mobile PWA not configured for port 8005")
                return False
    except Exception as e:
        print(f"❌ Mobile PWA config check failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 PTCC System Integration Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Students API", test_students_api),
        ("Briefing API", test_briefing_api),
        ("Mobile PWA Proxy", test_mobile_pwa_proxy),
        ("Desktop Web Config", test_desktop_web_config),
        ("Mobile PWA Config", test_mobile_pwa_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print("\n🌐 Access Points:")
        print("   • Backend API: http://localhost:8002")
        print("   • Desktop Web: http://localhost:8501")
        print("   • Mobile PWA: http://localhost:5173")
        print("\n📚 API Documentation: http://localhost:8002/docs")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)