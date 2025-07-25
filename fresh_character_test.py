#!/usr/bin/env python3
"""
Test with fresh chat history to isolate character reading issue
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def clear_and_test():
    # Login
    response = requests.post(f"{BASE_URL}/login", data={
        "username": "Demerzel",
        "password": "Seraphine"
    }, allow_redirects=False)
    cookies = response.cookies
    
    # Clear existing character info
    clear_data = {
        "ttrpg": "mouse-guard",
        "character_name": "",
        "character_stats": ""
    }
    requests.post(f"{BASE_URL}/api/character-info", json=clear_data, cookies=cookies)
    
    # Clear chat history by getting it and then using undo multiple times
    response = requests.get(
        f"{BASE_URL}/api/chat-history",
        params={"ttrpg": "mouse-guard"},
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        message_count = data.get("message_count", 0)
        
        # Undo all messages
        for i in range(message_count):
            requests.post(
                f"{BASE_URL}/api/chat-history/undo",
                json={"ttrpg": "mouse-guard"},
                cookies=cookies
            )
    
    # Now test with specific live values in a fresh conversation
    chat_data = {
        "message": "What character name do you see?",
        "page": "mouse-guard",
        "character_name": "FRESH_TEST_NAME_789",
        "character_stats": "FRESH_TEST_STATS_ABC"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get("response", "")
        print(f"AI Response: {ai_response}")
        
        if "FRESH_TEST_NAME_789" in ai_response:
            print("✅ SUCCESS: AI can see live textbox character name")
        else:
            print("❌ FAIL: AI cannot see live textbox character name")
            
        if "FRESH_TEST_STATS_ABC" in ai_response:
            print("✅ SUCCESS: AI can see live textbox character stats")
        else:
            print("❌ FAIL: AI cannot see live textbox character stats")
    else:
        print(f"Request failed: {response.status_code}")

if __name__ == "__main__":
    clear_and_test()
