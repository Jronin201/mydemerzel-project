#!/usr/bin/env python3
"""
Quick test to check if AI can see live textbox values
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def quick_test():
    # Login
    response = requests.post(f"{BASE_URL}/login", data={
        "username": "Demerzel",
        "password": "Seraphine"
    }, allow_redirects=False)
    cookies = response.cookies
    
    # Send chat with very specific live textbox values
    chat_data = {
        "message": "What character name do you see in my Character Information textbox right now?",
        "page": "mouse-guard",
        "character_name": "LIVE_TEST_CHARACTER_NAME_123",
        "character_stats": "LIVE_TEST_STATS_456"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get("response", "")
        print(f"AI Response: {ai_response}")
        
        if "LIVE_TEST_CHARACTER_NAME_123" in ai_response:
            print("✅ SUCCESS: AI can see live textbox character name")
        else:
            print("❌ FAIL: AI cannot see live textbox character name")
            
        if "LIVE_TEST_STATS_456" in ai_response:
            print("✅ SUCCESS: AI can see live textbox character stats")
        else:
            print("❌ FAIL: AI cannot see live textbox character stats")
    else:
        print(f"Request failed: {response.status_code}")

if __name__ == "__main__":
    quick_test()
