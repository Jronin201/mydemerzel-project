#!/usr/bin/env python3
"""
Test script to verify character information persistence in different scenarios
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

def test_character_info_persistence():
    """Test character information persistence across different TTRPGs"""
    print("🧪 Testing Character Information Persistence")
    print("=" * 50)
    
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
    
    # Test data for different TTRPGs
    test_scenarios = [
        {
            "ttrpg": "dune",
            "character_name": "Paul Atreides",
            "character_stats": "Duke's son with prescient abilities. Trained in the ways of the Bene Gesserit and the fighting methods of Duncan Idaho."
        },
        {
            "ttrpg": "the-one-ring", 
            "character_name": "Frodo Baggins",
            "character_stats": "A seasoned witcher mutagenically enhanced to hunt monsters. Trained with blades, signs, and alchemy. Stoic but driven by a personal code."
        },
        {
            "ttrpg": "call-of-cthulhu",
            "character_name": "Detective Sarah Williams",
            "character_stats": "Experienced investigator with a keen eye for detail. Has encountered the supernatural before and lived to tell the tale."
        }
    ]
    
    # Save character info for each TTRPG
    print("\n2. Saving character information for each TTRPG...")
    for scenario in test_scenarios:
        response = session.post(
            f"{BASE_URL}/api/character-info",
            json=scenario,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Saved character info for {scenario['ttrpg']}")
        else:
            print(f"❌ Failed to save character info for {scenario['ttrpg']}: {response.text}")
            return False
    
    # Verify each TTRPG maintains separate character info
    print("\n3. Verifying character information persistence and separation...")
    for scenario in test_scenarios:
        response = session.get(f"{BASE_URL}/api/character-info?ttrpg={scenario['ttrpg']}")
        
        if response.status_code == 200:
            data = response.json()
            
            if (data['character_name'] == scenario['character_name'] and 
                data['character_stats'] == scenario['character_stats']):
                print(f"✅ {scenario['ttrpg']}: Character info correctly persisted")
                print(f"   Character: {data['character_name'][:30]}...")
                print(f"   Stats: {data['character_stats'][:50]}...")
            else:
                print(f"❌ {scenario['ttrpg']}: Character info mismatch")
                print(f"   Expected: {scenario['character_name']}")
                print(f"   Got: {data['character_name']}")
                return False
        else:
            print(f"❌ Failed to load character info for {scenario['ttrpg']}")
            return False
    
    # Test updating existing character info
    print("\n4. Testing character information updates...")
    update_data = {
        "ttrpg": "dune",
        "character_name": "Paul Muad'Dib",
        "character_stats": "The prophesied Kwisatz Haderach, leader of the Fremen, Emperor of the Known Universe."
    }
    
    response = session.post(
        f"{BASE_URL}/api/character-info",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ Character info update request successful")
        
        # Verify the update
        response = session.get(f"{BASE_URL}/api/character-info?ttrpg=dune")
        if response.status_code == 200:
            data = response.json()
            if data['character_name'] == update_data['character_name']:
                print("✅ Character info successfully updated")
            else:
                print("❌ Character info update not reflected")
                return False
        else:
            print("❌ Failed to verify character info update")
            return False
    else:
        print(f"❌ Failed to update character info: {response.text}")
        return False
    
    # Verify other TTRPGs remain unchanged
    print("\n5. Verifying other TTRPGs remain unchanged...")
    for scenario in test_scenarios[1:]:  # Skip the first (Dune) which we updated
        response = session.get(f"{BASE_URL}/api/character-info?ttrpg={scenario['ttrpg']}")
        
        if response.status_code == 200:
            data = response.json()
            if data['character_name'] == scenario['character_name']:
                print(f"✅ {scenario['ttrpg']}: Unaffected by Dune update")
            else:
                print(f"❌ {scenario['ttrpg']}: Incorrectly modified")
                return False
        else:
            print(f"❌ Failed to verify {scenario['ttrpg']} remained unchanged")
            return False
    
    # Test character sessions API
    print("\n6. Testing character sessions API...")
    response = session.get(f"{BASE_URL}/api/character-sessions")
    
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        
        if len(sessions) >= 3:
            print(f"✅ Character sessions API working: {len(sessions)} sessions found")
            for session_info in sessions:
                print(f"   - {session_info['ttrpg_system']}: {session_info['character_name']}")
        else:
            print(f"❌ Expected at least 3 character sessions, got {len(sessions)}")
            return False
    else:
        print(f"❌ Character sessions API failed: {response.text}")
        return False
    
    print("\n🎉 All character information persistence tests passed!")
    print("✅ Character information is correctly persisted per user and per TTRPG")
    print("✅ Different TTRPGs maintain separate character information")
    print("✅ Updates work correctly without affecting other TTRPGs")
    print("✅ Character sessions API provides complete overview")
    
    return True


if __name__ == "__main__":
    try:
        success = test_character_info_persistence()
        if success:
            print("\n🚀 Character information persistence is working perfectly!")
            exit(0)
        else:
            print("\n💥 Character information persistence tests failed!")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://localhost:5000")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        exit(1)
