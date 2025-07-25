#!/usr/bin/env python3
"""
Test script to verify enhanced AI chatbot formatting functionality
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_formatting():
    """Test the enhanced formatting capabilities of the chatbot"""
    
    print("🎨 Testing Enhanced AI Chatbot Output Formatting")
    print("=" * 60)
    
    # Login first
    session = requests.Session()
    
    # Get the login page first to get session cookie
    get_login = session.get(f"{BASE_URL}/login")
    if get_login.status_code != 200:
        print(f"❌ Failed to access login page: {get_login.status_code}")
        return False
    
    login_response = session.post(f"{BASE_URL}/login", data={
        "username": "Demerzel",
        "password": "Seraphine"
    }, allow_redirects=False)
    
    if login_response.status_code not in [302, 200]:  # Redirect after successful login
        print(f"❌ Login failed with status: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}")
        return False
    
    print("✅ Successfully logged in")
    
    # Test cases for different formatting scenarios
    test_cases = [
        {
            "name": "Combat Scenario with Formatting",
            "message": "I attack the goblin with my sword! How much damage do I deal?",
            "page": "mouse-guard",
            "character_name": "Sir Brave - Level 3 Fighter",
            "character_stats": "HP: 25/25, Strength: 16, Dexterity: 14"
        },
        {
            "name": "Character Creation Request",
            "message": "Create a new Dune character for me with rich descriptions and formatting",
            "page": "dune",
            "character_name": "",
            "character_stats": ""
        },
        {
            "name": "Story Description with Multiple Elements",
            "message": "Describe the mysterious dungeon entrance with details about treasures, dangers, and magical effects",
            "page": "the-one-ring",
            "character_name": "Gandalf the Wise",
            "character_stats": "Wizard of great power, keeper of ancient secrets"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        chat_data = {
            "message": test_case["message"],
            "page": test_case["page"],
            "character_name": test_case["character_name"],
            "character_stats": test_case["character_stats"]
        }
        
        response = session.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "")
            
            print(f"📤 User Input: {test_case['message']}")
            print(f"📥 AI Response Preview: {ai_response[:200]}...")
            
            # Check for formatting elements
            formatting_checks = {
                "Has Bold Text": "**" in ai_response,
                "Has Italics": "*" in ai_response and "**" not in ai_response.replace("**", ""),
                "Has Emojis": any(ord(char) > 127 for char in ai_response),
                "Has Structured Content": any(marker in ai_response for marker in ["###", ">", "`", "- ", "• "]),
                "Has Character Updates": "[AI updated:" in ai_response,
            }
            
            print("🔍 Formatting Analysis:")
            for check_name, result in formatting_checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
            
            print(f"📊 Full Response Length: {len(ai_response)} characters")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Formatting Test Complete!")
    print("\n💡 To manually test:")
    print(f"1. Visit: {BASE_URL}")
    print("2. Login with: Demerzel / Seraphine")
    print("3. Select any TTRPG system")
    print("4. Ask for character creation or combat scenarios")
    print("5. Observe the colorful, formatted responses!")

if __name__ == "__main__":
    test_formatting()
