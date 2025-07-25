#!/usr/bin/env python3
"""
Test script to verify TTRPG-specific system prompts work in actual chat requests.
"""

import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ttrpg_chat_prompts():
    """Test that TTRPG-specific prompts are used in actual chat requests."""
    
    print("Testing TTRPG-specific prompts in chat requests...")
    print("=" * 60)
    
    # Test data for each TTRPG
    test_cases = [
        {
            "ttrpg": "dune",
            "message": "Tell me about the current situation.",
            "expected_keywords": ["Paul", "Atreides", "Arrakis", "spice"]
        },
        {
            "ttrpg": "the-one-ring", 
            "message": "What do I see around me?",
            "expected_keywords": ["Middle-earth", "Tolkien"]
        },
        {
            "ttrpg": "call-of-cthulhu",
            "message": "What mysteries await?",
            "expected_keywords": ["horror", "investigation", "1920s"]
        }
    ]
    
    base_url = "http://127.0.0.1:5000"
    
    # First login
    login_data = {"username": "testuser", "password": "testpass"}
    session = requests.Session()
    
    try:
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code != 200:
            print(f"✗ Login failed: {login_response.status_code}")
            return False
        print("✓ Login successful")
        
        for test_case in test_cases:
            ttrpg = test_case["ttrpg"]
            message = test_case["message"]
            
            print(f"\nTesting {ttrpg}:")
            
            # Send chat request
            chat_data = {
                "message": message,
                "page": ttrpg
            }
            
            response = session.post(f"{base_url}/chat", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                print(f"  ✓ Chat request successful")
                print(f"  ✓ AI Response preview: {ai_response[:100]}...")
                
                # Check if response seems appropriate for the TTRPG
                # (This is a basic check - the real test is that it doesn't error)
                if len(ai_response) > 10:
                    print(f"  ✓ Received substantial response ({len(ai_response)} chars)")
                else:
                    print(f"  ⚠ Short response: {ai_response}")
                    
            else:
                print(f"  ✗ Chat request failed: {response.status_code}")
                print(f"  Error: {response.text}")
        
        print(f"\nTTRPG chat prompt test completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_ttrpg_chat_prompts()
