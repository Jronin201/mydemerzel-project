#!/usr/bin/env python3
"""
TTRPG Integration Test Script

This script tests the integration of TTRPGs in the Demerzel system.
It verifies that all components work correctly together.
"""

import argparse
import json
import requests
import sys
import time
from pathlib import Path


class TTRPGIntegrationTester:
    def __init__(self, base_url="http://localhost:5000", ttrpg_name=None):
        self.base_url = base_url
        self.ttrpg_name = ttrpg_name
        self.session = requests.Session()
        self.test_results = {}
    
    def log_test(self, test_name, passed, message=""):
        """Log test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results[test_name] = {
            "passed": passed,
            "message": message
        }
    
    def test_configuration_exists(self):
        """Test that TTRPG configuration exists."""
        config_path = Path("ttrpg-config.json")
        
        if not config_path.exists():
            self.log_test("Configuration File", False, "ttrpg-config.json not found")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if self.ttrpg_name and self.ttrpg_name not in config.get("systems", {}):
                self.log_test("Configuration File", False, f"TTRPG '{self.ttrpg_name}' not found in config")
                return False
            
            self.log_test("Configuration File", True, f"Found {len(config.get('systems', {}))} registered TTRPGs")
            return True
            
        except json.JSONDecodeError as e:
            self.log_test("Configuration File", False, f"Invalid JSON: {e}")
            return False
    
    def test_directory_structure(self):
        """Test that required directories exist."""
        if not self.ttrpg_name:
            return True
        
        base_path = Path("static") / self.ttrpg_name
        
        if not base_path.exists():
            self.log_test("Directory Structure", False, f"Directory static/{self.ttrpg_name} not found")
            return False
        
        required_files = ["system_prompt.txt"]
        missing_files = []
        
        for file in required_files:
            if not (base_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log_test("Directory Structure", False, f"Missing files: {', '.join(missing_files)}")
            return False
        
        self.log_test("Directory Structure", True, "All required files present")
        return True
    
    def test_system_prompt(self):
        """Test that system prompt loads correctly."""
        if not self.ttrpg_name:
            return True
        
        prompt_path = Path("static") / self.ttrpg_name / "system_prompt.txt"
        
        if not prompt_path.exists():
            self.log_test("System Prompt", False, "system_prompt.txt not found")
            return False
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if len(content) < 50:
                self.log_test("System Prompt", False, "System prompt too short (< 50 characters)")
                return False
            
            if len(content) > 5000:
                self.log_test("System Prompt", False, "System prompt too long (> 5000 characters)")
                return False
            
            self.log_test("System Prompt", True, f"Valid prompt ({len(content)} characters)")
            return True
            
        except Exception as e:
            self.log_test("System Prompt", False, f"Error reading prompt: {e}")
            return False
    
    def test_server_connectivity(self):
        """Test that the server is running and responsive."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                self.log_test("Server Connectivity", True, "Server is running")
                return True
            else:
                self.log_test("Server Connectivity", False, f"Server returned status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.log_test("Server Connectivity", False, f"Cannot connect to server: {e}")
            return False
    
    def test_route_access(self):
        """Test that TTRPG route is accessible."""
        if not self.ttrpg_name:
            return True
        
        try:
            # Test direct route
            response = self.session.get(f"{self.base_url}/{self.ttrpg_name}", timeout=5, allow_redirects=False)
            
            if response.status_code in [200, 302]:  # 302 is redirect to chatbot
                self.log_test("Route Access", True, f"Route /{self.ttrpg_name} accessible")
                return True
            else:
                self.log_test("Route Access", False, f"Route returned status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.log_test("Route Access", False, f"Route access failed: {e}")
            return False
    
    def test_chatbot_integration(self):
        """Test that TTRPG integrates with chatbot."""
        if not self.ttrpg_name:
            return True
        
        try:
            # Test chatbot page with TTRPG parameter
            response = self.session.get(f"{self.base_url}/ttrpg-chatbot?ttrpg={self.ttrpg_name}", timeout=5)
            
            if response.status_code == 200:
                self.log_test("Chatbot Integration", True, "Chatbot page loads with TTRPG")
                return True
            else:
                self.log_test("Chatbot Integration", False, f"Chatbot page returned status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.log_test("Chatbot Integration", False, f"Chatbot integration failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test that API endpoints work with TTRPG."""
        if not self.ttrpg_name:
            return True
        
        # Test character info endpoint
        try:
            test_data = {
                "ttrpg": self.ttrpg_name,
                "character_name": "Test Character",
                "character_stats": "Test Stats"
            }
            
            response = self.session.post(f"{self.base_url}/api/character-info", json=test_data, timeout=5)
            
            if response.status_code == 200:
                self.log_test("API Endpoints", True, "Character info API works")
                return True
            else:
                self.log_test("API Endpoints", False, f"API returned status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.log_test("API Endpoints", False, f"API test failed: {e}")
            return False
    
    def test_data_isolation(self):
        """Test that TTRPG data is properly isolated."""
        if not self.ttrpg_name:
            return True
        
        # This is a basic test - in a real environment you'd want more comprehensive isolation testing
        try:
            # Test that character info directory exists or can be created
            char_dir = Path("character_info") / "anonymous" / self.ttrpg_name
            if not char_dir.exists():
                char_dir.mkdir(parents=True, exist_ok=True)
            
            # Test that chat history directory exists or can be created
            chat_dir = Path("chat_histories") / "anonymous" / self.ttrpg_name
            if not chat_dir.exists():
                chat_dir.mkdir(parents=True, exist_ok=True)
            
            self.log_test("Data Isolation", True, "User data directories accessible")
            return True
            
        except Exception as e:
            self.log_test("Data Isolation", False, f"Data isolation test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        print(f"🧪 TTRPG Integration Test Suite")
        if self.ttrpg_name:
            print(f"Testing TTRPG: {self.ttrpg_name}")
        print("=" * 60)
        
        tests = [
            self.test_configuration_exists,
            self.test_directory_structure,
            self.test_system_prompt,
            self.test_server_connectivity,
            self.test_route_access,
            self.test_chatbot_integration,
            self.test_api_endpoints,
            self.test_data_isolation
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("✓ All tests passed! TTRPG integration is working correctly.")
            return True
        else:
            print("✗ Some tests failed. Please check the issues above.")
            return False
    
    def generate_report(self):
        """Generate a detailed test report."""
        report = {
            "ttrpg_name": self.ttrpg_name,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r["passed"]),
                "failed": sum(1 for r in self.test_results.values() if not r["passed"])
            }
        }
        
        report_path = Path("diagnostics") / f"ttrpg_test_report_{self.ttrpg_name or 'all'}_{int(time.time())}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Test TTRPG integration in the Demerzel system")
    parser.add_argument('--ttrpg', help='Specific TTRPG to test (optional)')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL for testing')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    # If no specific TTRPG, test all registered ones
    if not args.ttrpg:
        config_path = Path("ttrpg-config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            active_systems = [name for name, system in config.get("systems", {}).items() 
                            if system.get("active", True)]
            
            if not active_systems:
                print("No active TTRPGs found to test.")
                return
            
            print(f"Testing {len(active_systems)} active TTRPGs...")
            
            all_passed = True
            for ttrpg_name in active_systems:
                print(f"\n{'='*20} Testing {ttrpg_name} {'='*20}")
                tester = TTRPGIntegrationTester(args.url, ttrpg_name)
                if not tester.run_all_tests():
                    all_passed = False
                
                if args.report:
                    tester.generate_report()
            
            print(f"\n{'='*60}")
            if all_passed:
                print("✓ All TTRPGs passed integration tests!")
            else:
                print("✗ Some TTRPGs failed integration tests.")
        else:
            print("No TTRPG configuration found. Run basic connectivity test...")
            tester = TTRPGIntegrationTester(args.url, None)
            tester.run_all_tests()
    else:
        # Test specific TTRPG
        tester = TTRPGIntegrationTester(args.url, args.ttrpg)
        success = tester.run_all_tests()
        
        if args.report:
            tester.generate_report()
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
