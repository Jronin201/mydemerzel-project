#!/usr/bin/env python3
"""
Comprehensive test for Character Information and Notes textbox read/write functionality.
This test verifies that the AI can properly read from and write to the character textboxes.
"""

import requests
import pytest
import json
import time
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "Demerzel"
TEST_TTRPG = "mouse-guard"

def test_login():
    """Test login functionality"""
    print("🔐 Testing login...")
    response = requests.post(f"{BASE_URL}/login", data={
        "username": "Demerzel",
        "password": "Seraphine"
    }, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ Login successful")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

@pytest.fixture()
def cookies():
    # obtain cookies once per test needing authenticated calls
    resp = requests.post(f"{BASE_URL}/login", data={"username":"Demerzel","password":"Seraphine"}, allow_redirects=False)
    assert resp.status_code in (200,302)
    return resp.cookies

def test_character_info_api(cookies):
    """Test the character info API endpoints"""
    print("\n📊 Testing Character Info API...")
    
    # Test GET (should be empty initially)
    response = requests.get(
        f"{BASE_URL}/api/character-info",
        params={"ttrpg": TEST_TTRPG},
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET character info successful: {data}")
    else:
        print(f"❌ GET character info failed: {response.status_code}")
        return False
    
    # Test POST (set some character info)
    test_char_data = {
        "ttrpg": TEST_TTRPG,
        "character_name": "Test Character - Bramble",
        "character_stats": "Test Stats - Fighter 3, Scout 2"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/character-info",
        json=test_char_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        print("✅ POST character info successful")
    else:
        print(f"❌ POST character info failed: {response.status_code}")
        return False
    
    # Test GET again (should now have our data)
    response = requests.get(
        f"{BASE_URL}/api/character-info",
        params={"ttrpg": TEST_TTRPG},
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("character_name") == test_char_data["character_name"]:
            print("✅ Character info persistence verified")
        else:
            print(f"❌ Character info mismatch: expected {test_char_data['character_name']}, got {data.get('character_name')}")
            return False
    else:
        print(f"❌ GET character info verification failed: {response.status_code}")
        return False
    
    return True

def test_chat_with_character_info(cookies):
    """Test that chat endpoint reads current character information from textboxes"""
    print("\n💬 Testing Chat with Character Info...")
    
    # Send a chat message with specific character info (simulating textbox content)
    chat_data = {
        "message": "What's in my Character Information textbox?",
        "page": TEST_TTRPG,
        "character_name": "Live Textbox Character - Thistle",
        "character_stats": "Live Textbox Stats - Pathfinder 4, Scout 3"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=chat_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get("response", "")
        print(f"✅ Chat response received: {ai_response[:200]}...")
        
        # Check if AI can see the live textbox values
        if "Thistle" in ai_response and "Pathfinder 4" in ai_response:
            print("✅ AI successfully read live textbox character information")
            return True
        else:
            print(f"❌ AI did not see live textbox values. Response: {ai_response}")
            return False
    else:
        print(f"❌ Chat request failed: {response.status_code}")
        return False

def test_character_creation_and_update(cookies):
    """Test that AI can create characters and automatically update textboxes"""
    print("\n🎭 Testing Character Creation and Auto-Update...")
    
    # Clear existing character info first
    clear_data = {
        "ttrpg": TEST_TTRPG,
        "character_name": "",
        "character_stats": ""
    }
    requests.post(f"{BASE_URL}/api/character-info", json=clear_data, cookies=cookies)
    
    # Ask AI to create a character
    chat_data = {
        "message": "Create a Mouse Guard character for me with full details and add it to the Character Information textbox.",
        "page": TEST_TTRPG,
        "character_name": "",
        "character_stats": ""
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=chat_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get("response", "")
        print(f"✅ Character creation response: {ai_response[:300]}...")
        
        # Wait a moment for update to process
        time.sleep(1)
        
        # Check if character info was actually updated
        response = requests.get(
            f"{BASE_URL}/api/character-info",
            params={"ttrpg": TEST_TTRPG},
            cookies=cookies
        )
        
        if response.status_code == 200:
            char_data = response.json()
            if char_data.get("character_name") and len(char_data.get("character_name", "")) > 0:
                print(f"✅ Character automatically created and saved: {char_data.get('character_name')}")
                return True
            else:
                print(f"❌ No character information was saved after creation request")
                print(f"   Character name: '{char_data.get('character_name', 'EMPTY')}'")
                print(f"   Character stats: '{char_data.get('character_stats', 'EMPTY')}'")
                return False
        else:
            print(f"❌ Could not verify character creation: {response.status_code}")
            return False
    else:
        print(f"❌ Character creation request failed: {response.status_code}")
        return False

def test_live_textbox_vs_stored_priority(cookies):
    """Test that live textbox values take priority over stored values"""
    print("\n⚖️ Testing Live Textbox vs Stored Data Priority...")
    
    # First, store some character info via API
    stored_data = {
        "ttrpg": TEST_TTRPG,
        "character_name": "STORED Character - Oak",
        "character_stats": "STORED Stats - Will 4, Health 5"
    }
    requests.post(f"{BASE_URL}/api/character-info", json=stored_data, cookies=cookies)
    
    # Then send a chat with different live textbox values
    chat_data = {
        "message": "Tell me about my character",
        "page": TEST_TTRPG,
        "character_name": "LIVE Character - Willow",
        "character_stats": "LIVE Stats - Nature 3, Fighter 2"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=chat_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get("response", "")
        print(f"✅ Priority test response: {ai_response[:200]}...")
        
        # AI should see LIVE values, not STORED values
        if "Willow" in ai_response and "Oak" not in ai_response:
            print("✅ Live textbox values correctly take priority")
            return True
        elif "Oak" in ai_response and "Willow" not in ai_response:
            print("❌ AI using stored values instead of live textbox values")
            return False
        else:
            print(f"❌ Unclear which values AI is using. Response: {ai_response}")
            return False
    else:
        print(f"❌ Priority test failed: {response.status_code}")
        return False

def run_all_tests():
    """Run all character textbox integration tests"""
    print("🧪 Starting Comprehensive Character Textbox Integration Tests")
    print("=" * 60)
    
    # Test login
    cookies = test_login()
    if not cookies:
        print("❌ Cannot proceed without login")
        return False
    
    # Run all tests
    tests = [
        test_character_info_api,
        test_chat_with_character_info,
        test_character_creation_and_update,
        test_live_textbox_vs_stored_priority
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func(cookies)
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Character textbox integration is working!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Character textbox integration needs fixes")
        return False

if __name__ == "__main__":
    # Check if Flask app is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Flask app is not running. Start it with: python3 app.py")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)
