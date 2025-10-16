#!/usr/bin/env python3
"""
Simple backend test script to verify core functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all backend modules can be imported"""
    try:
        from backend.core.database import check_database_health, get_database_stats
        from backend.core.briefing_engine import generate_daily_briefing
        from backend.models.database_models import Student
        print("✅ All backend imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connectivity"""
    try:
        from backend.core.database import check_database_health, get_database_stats

        health = check_database_health()
        if health['status'] == 'healthy':
            print("✅ Database connection successful")

            stats = get_database_stats()
            print(f"✅ Database stats: {stats}")

            return True
        else:
            print(f"❌ Database health check failed: {health}")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_students():
    """Test student data access"""
    try:
        from sqlalchemy.orm import Session
        from backend.models.database_models import Student
        from backend.core.database import SessionLocal

        db = SessionLocal()
        try:
            students = db.query(Student).limit(5).all()

            if students:
                print(f"✅ Found {len(students)} students in database")
                for student in students[:3]:  # Show first 3
                    print(f"  - {student.name} ({student.class_code})")
                return True
            else:
                print("❌ No students found in database")
                return False
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Student test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PTCC Backend Components")
    print("=" * 40)

    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Student Data Test", test_students),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 40)
    print("📊 Test Results:")

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All backend tests passed!")
        print("✅ Core functionality is working")
        print("📝 Backend server issue may be with HTTP startup only")
    else:
        print("⚠️  Some tests failed - backend needs debugging")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)