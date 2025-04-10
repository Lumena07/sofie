#!/usr/bin/env python
"""
Test runner for Sofie.
This script runs all the tests for the Sofie application.
"""

import os
import sys
import subprocess
import time

def run_test(test_name, test_script):
    """Run a test script and return the result."""
    print(f"\n{'=' * 80}")
    print(f"Running {test_name}...")
    print(f"{'=' * 80}\n")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, test_script], capture_output=False)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\nTest completed in {duration:.2f} seconds")
    
    return result.returncode == 0

def main():
    """Run all tests."""
    tests = [
        ("Google Drive Integration", "test_drive_integration.py"),
        ("Document Processing", "test_document_processing.py"),
        ("OpenAI Integration", "test_openai_integration.py"),
        ("Knowledge Base", "test_knowledge_base.py")
    ]
    
    results = []
    for test_name, test_script in tests:
        if os.path.exists(test_script):
            success = run_test(test_name, test_script)
            results.append((test_name, success))
        else:
            print(f"❌ Test script not found: {test_script}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary:")
    print("=" * 80)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not success:
            all_passed = False
    
    print("=" * 80)
    if all_passed:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 