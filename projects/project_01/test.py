#!/usr/bin/env python3
"""
Tests for Project 1: Personal Information Card
"""
import sys
import subprocess
import importlib.util

def test_project():
    """Run tests on the personal info card project."""
    print("🧪 Testing Personal Info Card Project...")
    
    try:
        # Import the student's code
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        print("✅ Code imports successfully")
        
        # Test that main function exists
        if hasattr(main_module, 'main'):
            print("✅ main() function exists")
        else:
            print("❌ main() function missing")
            return False
        
        # Run the program and capture output
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Program crashed: {result.stderr}")
            return False
        
        output = result.stdout
        
        # Check for required elements
        tests_passed = 0
        total_tests = 6
        
        if "PERSONAL INFO CARD" in output:
            print("✅ Has card title")
            tests_passed += 1
        else:
            print("❌ Missing card title")
        
        if "Name:" in output:
            print("✅ Shows name field")
            tests_passed += 1
        else:
            print("❌ Missing name field")
        
        if "Age:" in output:
            print("✅ Shows age field")
            tests_passed += 1
        else:
            print("❌ Missing age field")
        
        if "Email:" in output or "Favorite Language:" in output:
            print("✅ Shows additional fields")
            tests_passed += 1
        else:
            print("❌ Missing additional personal fields")
        
        if "Fun Fact:" in output:
            print("✅ Shows fun fact")
            tests_passed += 1
        else:
            print("❌ Missing fun fact field")
        
        if len(output.strip()) > 100:
            print("✅ Has substantial output")
            tests_passed += 1
        else:
            print("❌ Output seems too short")
        
        print(f"\n📊 Tests passed: {tests_passed}/{total_tests}")
        
        print("\n📄 Your program output:")
        print("=" * 40)
        print(output)
        print("=" * 40)
        
        if tests_passed >= 4:
            print("🎉 Great job! Your personal info card is working!")
            return True
        else:
            print("🔧 Keep working - you're getting there!")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = test_project()
    sys.exit(0 if success else 1)
