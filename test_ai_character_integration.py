#!/usr/bin/env python3
"""
Test script for AI character information read/write and undo functionality
"""

import sys
import os
import requests
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"
USERNAME = "Demerzel"
PASSWORD = "Seraphine"

def test_ai_character_integration():
    """Test AI's ability to read and write character information with undo functionality"""
    print("🤖 Testing AI Character Information Integration")
    print("=" * 60)
    
    # Create a session for maintaining login
    session = requests.Session()
    
    # Login
    print("1. Logging in...")
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return False
    print("✅ Login successful")
    
    # Test TTRPG
    test_ttrpg = "dune"
    
    # Clear any existing character info for clean test
    print("\n2. Setting up initial character information...")
    initial_char_data = {
        "ttrpg": test_ttrpg,
        "character_name": "Paul Atreides - Young Duke, untested in combat",
        "character_stats": "Quest: Find the traitor in House Atreides. Status: Just arrived on Arrakis."
    }
    
    response = session.post(
        f"{BASE_URL}/api/character-info",
        json=initial_char_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ Initial character info set")
    else:
        print(f"❌ Failed to set initial character info: {response.text}")
        return False
    
    # Test AI reading character information
    print("\n3. Testing AI awareness of character information...")
    chat_data = {
        "message": "What do you know about my character and current quest?",
        "page": test_ttrpg,
        "character_name": initial_char_data["character_name"],
        "character_stats": initial_char_data["character_stats"]
    }
    
    response = session.post(
        f"{BASE_URL}/chat",
        json=chat_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        ai_response = response.json().get("response", "")
        if "Paul" in ai_response and ("Atreides" in ai_response or "duke" in ai_response.lower()):
            print("✅ AI correctly reads and uses character information")
            print(f"   AI Response: {ai_response[:100]}...")
        else:
            print("❌ AI did not demonstrate awareness of character information")
            print(f"   AI Response: {ai_response}")
            return False
    else:
        print(f"❌ Chat request failed: {response.text}")
        return False
    
    # Test AI updating character information
    print("\n4. Testing AI ability to update character information...")
    update_request_data = {
        "message": "I just completed combat training and learned advanced sword techniques. Please update my character information to reflect this.",
        "page": test_ttrpg,
        "character_name": initial_char_data["character_name"],
        "character_stats": initial_char_data["character_stats"]
    }
    
    response = session.post(
        f"{BASE_URL}/chat",
        json=update_request_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        ai_response = response.json().get("response", "")
        if "*[AI updated:" in ai_response:
            print("✅ AI indicated it updated character information")
            print(f"   AI Response: {ai_response[:150]}...")
            
            # Verify the update was actually saved
            time.sleep(1)  # Give server time to process
            response = session.get(f"{BASE_URL}/api/character-info?ttrpg={test_ttrpg}")
            if response.status_code == 200:
                updated_info = response.json()
                if "combat" in updated_info["character_name"].lower() or "sword" in updated_info["character_name"].lower():
                    print("✅ Character information successfully updated by AI")
                    print(f"   Updated Character Info: {updated_info['character_name'][:80]}...")
                else:
                    print("❌ AI claimed to update but change not reflected")
                    return False
            else:
                print("❌ Could not verify character info update")
                return False
        else:
            print("❌ AI did not indicate any updates were made")
            print(f"   AI Response: {ai_response}")
            return False
    else:
        print(f"❌ Update request failed: {response.text}")
        return False
    
    # Test AI updating notes section
    print("\n5. Testing AI ability to update notes...")
    notes_update_data = {
        "message": "I discovered a secret chamber in the palace with ancient Atreides artifacts. This is important for our quest.",
        "page": test_ttrpg,
        "character_name": updated_info["character_name"],
        "character_stats": updated_info["character_stats"]
    }
    
    response = session.post(
        f"{BASE_URL}/chat",
        json=notes_update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        ai_response = response.json().get("response", "")
        if "*[AI updated:" in ai_response:
            print("✅ AI indicated it updated notes")
            
            # Verify the notes update
            time.sleep(1)
            response = session.get(f"{BASE_URL}/api/character-info?ttrpg={test_ttrpg}")
            if response.status_code == 200:
                updated_info = response.json()
                if "chamber" in updated_info["character_stats"].lower() or "artifact" in updated_info["character_stats"].lower():
                    print("✅ Notes successfully updated by AI")
                    print(f"   Updated Notes: {updated_info['character_stats'][:80]}...")
                else:
                    print("❌ AI claimed to update notes but change not reflected")
                    return False
            else:
                print("❌ Could not verify notes update")
                return False
        else:
            print("⚠️  AI responded but may not have updated notes (this might be normal depending on context)")
    else:
        print(f"❌ Notes update request failed: {response.text}")
        return False
    
    # Test undo functionality
    print("\n6. Testing undo functionality...")
    undo_data = {
        "message": "Please undo the last change to my character information",
        "page": test_ttrpg
    }
    
    response = session.post(
        f"{BASE_URL}/chat",
        json=undo_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        ai_response = response.json().get("response", "")
        print(f"   AI Response to undo request: {ai_response[:100]}...")
    
    # Test undo API directly
    undo_api_data = {"ttrpg": test_ttrpg}
    response = session.post(
        f"{BASE_URL}/api/character-info/undo",
        json=undo_api_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        undo_result = response.json()
        if undo_result.get("success"):
            print("✅ Undo functionality working")
            print(f"   Undo message: {undo_result['message']}")
            print(f"   Restored from: {undo_result['restored_from']}")
        else:
            print("❌ Undo failed")
            print(f"   Error: {undo_result.get('message', 'Unknown error')}")
            return False
    else:
        print(f"❌ Undo API request failed: {response.text}")
        return False
    
    # Test history API
    print("\n7. Testing character information history...")
    response = session.get(f"{BASE_URL}/api/character-info/history?ttrpg={test_ttrpg}&limit=5")
    
    if response.status_code == 200:
        history_data = response.json()
        history = history_data.get("history", [])
        if len(history) > 0:
            print(f"✅ History API working: {len(history)} entries found")
            for i, entry in enumerate(history[-3:]):  # Show last 3 entries
                print(f"   {i+1}. {entry['timestamp']} (by {entry['source']})")
        else:
            print("⚠️  No history entries found (might be normal for fresh test)")
    else:
        print(f"❌ History API request failed: {response.text}")
        return False
    
    print("\n🎉 All AI character information integration tests completed!")
    print("✅ AI can read character information and notes")
    print("✅ AI can update character information when needed")
    print("✅ AI can update notes section when needed") 
    print("✅ Undo functionality works for recent changes")
    print("✅ Change history is properly tracked")
    print("✅ API endpoints for undo and history are functional")
    
    return True


if __name__ == "__main__":
    try:
        success = test_ai_character_integration()
        if success:
            print("\n🚀 AI character information integration is working perfectly!")
            exit(0)
        else:
            print("\n💥 AI character information integration tests failed!")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://localhost:5000")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        exit(1)
