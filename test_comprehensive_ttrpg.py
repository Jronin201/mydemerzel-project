#!/usr/bin/env python3
"""
Comprehensive test to verify TTRPG-specific system prompts are working correctly.
"""

import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import load_system_prompt

def test_comprehensive_ttrpg_system():
    """Comprehensive test of TTRPG-specific system prompt functionality."""
    
    print("🧪 COMPREHENSIVE TTRPG SYSTEM PROMPT TEST")
    print("=" * 80)
    
    # 1. Test prompt loading
    print("1️⃣  Testing System Prompt Loading...")
    print("-" * 40)
    
    ttrpgs = {
        "dune": {
            "keywords": ["Dune", "spice", "Atreides", "Game Master", "political", "espionage"],
            "title": "Dune: Adventures in the Imperium"
        },
        "the-one-ring": {
            "keywords": ["Middle-earth", "Tolkien", "Loremaster", "Fellowship"],
            "title": "The Witcher"
        },
        "call-of-cthulhu": {
            "keywords": ["Lovecraft", "cosmic horror", "Keeper", "sanity", "1920s"],
            "title": "Zweihander"
        }
    }
    
    global_prompt = load_system_prompt("")
    print(f"   ✓ Global prompt: {len(global_prompt)} chars")
    
    for ttrpg, info in ttrpgs.items():
        prompt = load_system_prompt(ttrpg)
        print(f"   ✓ {info['title']}: {len(prompt)} chars")
        
        # Check for expected keywords
        found = [kw for kw in info['keywords'] if kw in prompt]
        missing = [kw for kw in info['keywords'] if kw not in prompt]
        
        if found:
            print(f"     Keywords found: {', '.join(found)}")
        if missing:
            print(f"     ⚠ Missing keywords: {', '.join(missing)}")
    
    # 2. Test chat integration
    print(f"\n2️⃣  Testing Chat Integration...")
    print("-" * 40)
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Login
        login_data = {"username": "testuser", "password": "testpass"}
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"   ✗ Login failed: {login_response.status_code}")
            return False
        
        print("   ✓ Login successful")
        
        # Test each TTRPG with setting-appropriate questions
        test_messages = {
            "dune": "What political factions should I be aware of?",
            "the-one-ring": "What ancient paths lie before us?", 
            "call-of-cthulhu": "What strange whispers echo in this old mansion?"
        }
        
        for ttrpg, message in test_messages.items():
            print(f"\n   Testing {ttrpgs[ttrpg]['title']}:")
            
            chat_data = {"message": message, "page": ttrpg}
            response = session.post(f"{base_url}/chat", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                print(f"     ✓ Response received ({len(ai_response)} chars)")
                print(f"     Preview: {ai_response[:80]}...")
                
                # Basic quality checks
                if len(ai_response) > 50:
                    print("     ✓ Substantial response")
                else:
                    print("     ⚠ Short response")
                    
                # Check for obvious cross-contamination
                other_ttrpgs = [t for t in ttrpgs.keys() if t != ttrpg]
                contamination = []
                
                for other in other_ttrpgs:
                    other_keywords = ttrpgs[other]['keywords']
                    found_other = [kw for kw in other_keywords if kw.lower() in ai_response.lower()]
                    if found_other:
                        contamination.extend(found_other)
                
                if contamination:
                    print(f"     ⚠ Possible cross-contamination: {', '.join(contamination)}")
                else:
                    print("     ✓ No obvious cross-contamination")
                    
            else:
                print(f"     ✗ Chat failed: {response.status_code}")
                print(f"     Error: {response.text}")
        
        # 3. Test character information isolation
        print(f"\n3️⃣  Testing Character Information Isolation...")
        print("-" * 40)
        
        # Set different character info for each TTRPG
        char_data = {
            "dune": {
                "character_name": "Paul Atreides - Duke of Arrakis",
                "character_stats": "Quest: Uncover the traitor. Status: On Arrakis."
            },
            "the-one-ring": {
                "character_name": "Brego - Ranger of the North",
                "character_stats": "Quest: Protect the Shire. Status: Traveling through Mirkwood."
            },
            "call-of-cthulhu": {
                "character_name": "Dr. Henry Armitage - Miskatonic Professor",
                "character_stats": "Investigation: Strange disappearances. Status: Researching ancient texts."
            }
        }
        
        # Set character info for each TTRPG
        for ttrpg, char_info in char_data.items():
            char_request = {
                "ttrpg": ttrpg,
                **char_info
            }
            
            response = session.post(f"{base_url}/api/character-info", json=char_request)
            if response.status_code == 200:
                print(f"   ✓ Character info set for {ttrpgs[ttrpg]['title']}")
            else:
                print(f"   ✗ Failed to set character info for {ttrpg}")
        
        # Test that each TTRPG uses its own character info
        for ttrpg in ttrpgs.keys():
            message = "What do you know about my character?"
            chat_data = {"message": message, "page": ttrpg}
            response = session.post(f"{base_url}/chat", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                
                # Check if the response contains the correct character name
                expected_char = char_data[ttrpg]["character_name"].split(" - ")[0]
                if expected_char in ai_response:
                    print(f"   ✓ {ttrpgs[ttrpg]['title']} uses correct character: {expected_char}")
                else:
                    print(f"   ⚠ {ttrpgs[ttrpg]['title']} may not be using correct character")
                    print(f"     Expected: {expected_char}, Response: {ai_response[:100]}...")
        
        print(f"\n🎉 COMPREHENSIVE TEST COMPLETED!")
        print("=" * 80)
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to server. Make sure Flask app is running.")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_comprehensive_ttrpg_system()
