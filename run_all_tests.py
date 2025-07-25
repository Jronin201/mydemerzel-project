#!/usr/bin/env python3
"""
Comprehensive Test Runner for TTRPG Chatbot
Runs all test*.py files in the root directory and reports results
"""

import subprocess
import sys
import os
import time
from datetime import datetime

# List of all test files in the root directory
test_files = [
    'test_ai_character_integration.py',
    'test_app_invalid_json.py', 
    'test_character_integration.py',
    'test_character_live.py',
    'test_character_persistence.py',
    'test_character_textbox_functionality.py',
    'test_character_textbox_integration.py',
    'test_character_update.py',
    'test_character_updates.py',
    'test_chat_history.py',
    'test_comprehensive_ttrpg.py',
    'test_final_greeting.py',
    'test_final_integration.py',
    'test_full_app.py',
    'test_greeting_system.py',
    'test_integration.py',
    'test_interface_updates.py',
    'test_lockdown_integration.py',
    'test_memory_optimization.py',
    'test_mouse_guard.py',
    'test_mouse_guard_knowledge.py',
    'test_mouse_guard_loading.py',
    'test_one_ring_character.py',
    'test_optimized_embeddings.py',
    'test_optimized_search.py',
    'test_system_prompts.py',
    'test_token_counter.py',
    'test_ttrpg_chat_integration.py',
    'test_ttrpg_tracking.py',
    'test_unlimited_characters.py'
]

def run_test(test_file):
    """Run a single test file and capture output"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Use the configured Python environment
        result = subprocess.run([
            '/home/codespace/.python/current/bin/python', 
            test_file
        ], 
        capture_output=True, 
        text=True, 
        timeout=300,  # 5 minute timeout
        cwd='/workspaces/mydemerzel-project'
        )
        
        print(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"📥 STDERR:\n{result.stderr}")
        
        return {
            'file': test_file,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'status': 'PASSED' if result.returncode == 0 else 'FAILED'
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: Test {test_file} took longer than 5 minutes")
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out after 5 minutes',
            'status': 'TIMEOUT'
        }
    except Exception as e:
        print(f"❌ ERROR: Failed to run {test_file}: {str(e)}")
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'status': 'ERROR'
        }

def main():
    """Run all tests and generate summary report"""
    print(f"🚀 TTRPG Chatbot Test Runner")
    print(f"{'='*60}")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Total tests to run: {len(test_files)}")
    print(f"{'='*60}")
    
    results = []
    
    # Run each test
    for test_file in test_files:
        if os.path.exists(test_file):
            result = run_test(test_file)
            results.append(result)
            time.sleep(1)  # Brief pause between tests
        else:
            print(f"⚠️  WARNING: {test_file} not found, skipping...")
            results.append({
                'file': test_file,
                'returncode': -1,
                'stdout': '',
                'stderr': 'File not found',
                'status': 'NOT_FOUND'
            })
    
    # Generate summary report
    print(f"\n{'='*80}")
    print(f"📊 TEST SUMMARY REPORT")
    print(f"{'='*80}")
    
    passed = [r for r in results if r['status'] == 'PASSED']
    failed = [r for r in results if r['status'] == 'FAILED']
    errors = [r for r in results if r['status'] in ['ERROR', 'TIMEOUT', 'NOT_FOUND']]
    
    print(f"✅ PASSED:   {len(passed):2d} tests")
    print(f"❌ FAILED:   {len(failed):2d} tests")
    print(f"⚠️  ERRORS:   {len(errors):2d} tests")
    print(f"📋 TOTAL:    {len(results):2d} tests")
    
    if failed:
        print(f"\n❌ FAILED TESTS:")
        for result in failed:
            print(f"   • {result['file']}")
            if result['stderr']:
                # Show first few lines of error
                error_lines = result['stderr'].split('\n')[:3]
                for line in error_lines:
                    if line.strip():
                        print(f"     └─ {line.strip()}")
    
    if errors:
        print(f"\n⚠️  ERROR TESTS:")
        for result in errors:
            print(f"   • {result['file']} - {result['status']}")
            if result['stderr']:
                print(f"     └─ {result['stderr']}")
    
    if passed:
        print(f"\n✅ PASSED TESTS:")
        for result in passed:
            print(f"   • {result['file']}")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Return exit code based on results
    if failed or errors:
        return 1
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
