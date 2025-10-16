#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify PTTC system is working
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database():
    """Test database connection and tables"""
    print("Testing database...")
    
    try:
        from backend.core.database import create_tables, check_database_health
        from backend.core.logging_config import setup_logging
        
        setup_logging()
        
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Check health
        health = check_database_health()
        if health['status'] == 'healthy':
            print("✅ Database connection healthy")
        else:
            print(f"❌ Database unhealthy: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_sample_data():
    """Test sample data import"""
    print("\nTesting sample data import...")
    
    try:
        from backend.scripts.import_sample import main as import_sample
        
        # Import sample data
        import_sample()
        print("✅ Sample data imported successfully")
        
    except Exception as e:
        print(f"❌ Sample data import failed: {e}")
        return False
    
    return True

def test_briefing_engine():
    """Test briefing engine"""
    print("\nTesting briefing engine...")
    
    try:
        from backend.core.briefing_engine import generate_daily_briefing
        
        # Generate briefing
        briefing = generate_daily_briefing()
        print(f"✅ Briefing generated for {briefing.date}")
        print(f"   - Classes today: {briefing.classes_today}")
        print(f"   - Total students: {briefing.total_students}")
        
    except Exception as e:
        print(f"❌ Briefing engine test failed: {e}")
        return False
    
    return True

def test_rag_engine():
    """Test RAG engine"""
    print("\nTesting RAG engine...")
    
    try:
        from backend.core.rag_engine import get_rag_engine
        
        # Initialize RAG engine
        rag_engine = get_rag_engine()
        print("✅ RAG engine initialized")
        
        # Index database data
        rag_engine.index_database_data()
        print("✅ Database data indexed for search")
        
        # Test search
        results = rag_engine.search("student", limit=5)
        print(f"✅ Search returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ RAG engine test failed: {e}")
        return False
    
    return True

def test_api():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        import requests
        import time
        import subprocess
        
        # Start API server in background
        print("Starting API server...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        time.sleep(3)
        
        try:
            # Test health endpoint
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API health check passed")
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
            
            # Test briefing endpoint
            response = requests.get("http://localhost:8000/api/briefing/today", timeout=5)
            if response.status_code == 200:
                print("✅ API briefing endpoint working")
            else:
                print(f"❌ API briefing endpoint failed: {response.status_code}")
                return False
            
            # Test search endpoint
            response = requests.get("http://localhost:8000/api/search/?q=student", timeout=5)
            if response.status_code == 200:
                print("✅ API search endpoint working")
            else:
                print(f"❌ API search endpoint failed: {response.status_code}")
                return False
                
        finally:
            # Stop API server
            api_process.terminate()
            api_process.wait()
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🏫 PTCC System Test")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("Sample Data", test_sample_data),
        ("Briefing Engine", test_briefing_engine),
        ("RAG Engine", test_rag_engine),
        ("API", test_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! PTCC is ready to use.")
        print("\nTo start the system:")
        print("1. Backend: cd backend && python main.py")
        print("2. Frontend: cd frontend/desktop-web && python run.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())