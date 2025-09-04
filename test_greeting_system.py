#!/usr/bin/env python3
"""
Test the new initial greeting and character creation flow for all TTRPGs.
"""

import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_initial_greeting_system():
    """Test the new initial greeting and character creation flow."""
    
    print("🎭 TESTING INITIAL GREETING & CHARACTER CREATION SYSTEM")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Login
        print("1️⃣  Logging in...")
        login_data = {"username": "testuser_greeting", "password": "testpass"}
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"   ✗ Login failed: {login_response.status_code}")
            return False
        
        print("   ✓ Login successful")
        
        # Test each TTRPG for initial greeting
        ttrpgs = {
            "dune": "Dune: Adventures in the Imperium",
            "the-one-ring": "The Witcher",
        "call-of-cthulhu": "Zweihander"
        }
        
        for ttrpg, title in ttrpgs.items():
            print(f"\n2️⃣  Testing {title} Initial Greeting...")
            
            # Send any initial message to trigger greeting
            test_data = {"message": "hello", "page": ttrpg}
            response = session.post(f"{base_url}/chat", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                greeting = result.get("response", "")
                print(f"   ✓ Received greeting: {greeting[:80]}...")
                
                # Check if greeting contains appropriate welcome content
                if "welcome" in greeting.lower() or "campaign" in greeting.lower():
                    print("   ✓ Contains appropriate welcome content")
                else:
                    print("   ⚠ May not contain proper welcome content")
                
                # Test campaign start response
                print(f"   Testing campaign start flow...")
                start_data = {"message": "Yes, I'd like to start a campaign", "page": ttrpg}
                start_response = session.post(f"{base_url}/chat", json=start_data)
                
                if start_response.status_code == 200:
                    start_result = start_response.json()
                    start_reply = start_result.get("response", "")
                    print(f"   ✓ Campaign start response: {start_reply[:80]}...")
                    
                    # Check for character creation prompts
                    char_keywords = ["character", "create", "information", "field"]
                    found_keywords = [kw for kw in char_keywords if kw.lower() in start_reply.lower()]
                    
                    if found_keywords:
                        print(f"   ✓ Contains character creation guidance: {', '.join(found_keywords)}")
                    else:
                        print("   ⚠ May not contain character creation guidance")
                else:
                    print(f"   ✗ Campaign start test failed: {start_response.status_code}")
            else:
                print(f"   ✗ Initial greeting test failed: {response.status_code}")
        
        print(f"\n🎉 Initial greeting system test completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to server. Make sure Flask app is running.")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_initial_greeting_system()
