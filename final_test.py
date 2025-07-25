#!/usr/bin/env python3
"""
Final comprehensive test
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def final_test():
    # Login
    response = requests.post(f"{BASE_URL}/login", data={
        "username": "Demerzel",
        "password": "Seraphine"
    }, allow_redirects=False)
    cookies = response.cookies
    
    # Clear everything
    clear_data = {"ttrpg": "mouse-guard", "character_name": "", "character_stats": ""}
    requests.post(f"{BASE_URL}/api/character-info", json=clear_data, cookies=cookies)
    
    # Test 1: Can AI see live character name?
    chat_data = {
        "message": "What character name do you see in my Character Information textbox?",
        "page": "mouse-guard",
        "character_name": "TEST_CHAR_NAME_XYZ",
        "character_stats": "TEST_CHAR_STATS_123"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, cookies=cookies)
    ai_response = response.json().get("response", "")
    print(f"Test 1 - Character Name Recognition:")
    print(f"Response: {ai_response}")
    print(f"✅ SUCCESS" if "TEST_CHAR_NAME_XYZ" in ai_response else "❌ FAIL")
    print()
    
    # Test 2: Can AI see live character stats?
    chat_data2 = {
        "message": "What character stats or notes do you see?",
        "page": "mouse-guard",
        "character_name": "TEST_CHAR_NAME_XYZ",
        "character_stats": "TEST_CHAR_STATS_123"
    }
    
    response2 = requests.post(f"{BASE_URL}/chat", json=chat_data2, cookies=cookies)
    ai_response2 = response2.json().get("response", "")
    print(f"Test 2 - Character Stats Recognition:")
    print(f"Response: {ai_response2}")
    print(f"✅ SUCCESS" if "TEST_CHAR_STATS_123" in ai_response2 else "❌ FAIL")
    print()
    
    # Test 3: Character creation and auto-update
    chat_data3 = {
        "message": "Create a new Mouse Guard character and put it in the Character Information textbox.",
        "page": "mouse-guard",
        "character_name": "",
        "character_stats": ""
    }
    
    response3 = requests.post(f"{BASE_URL}/chat", json=chat_data3, cookies=cookies)
    ai_response3 = response3.json().get("response", "")
    print(f"Test 3 - Character Creation:")
    print(f"Response: {ai_response3[:200]}...")
    
    # Check if character was actually saved
    import time
    time.sleep(1)
    response4 = requests.get(f"{BASE_URL}/api/character-info", params={"ttrpg": "mouse-guard"}, cookies=cookies)
    char_data = response4.json()
    print(f"Character saved: {bool(char_data.get('character_name'))}")
    print(f"✅ SUCCESS" if char_data.get('character_name') else "❌ FAIL")

if __name__ == "__main__":
    final_test()
