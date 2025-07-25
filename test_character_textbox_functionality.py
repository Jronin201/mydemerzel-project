#!/usr/bin/env python3
"""
Test to verify that the AI can properly read and write from Character Information and Notes textboxes.
This test simulates the chat flow and checks that character information is being processed correctly.
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, load_user_character_info, save_user_character_info

def test_character_info_processing():
    """Test that character information is properly included in the chat flow"""
    print("🧪 Testing Character Information Processing...")
    
    with app.test_client() as client:
        # Login first
        login_response = client.post('/login', data={
            'username': 'Demerzel',
            'password': 'Seraphine'
        }, follow_redirects=True)
        
        print(f"✅ Login successful: {login_response.status_code == 200}")
        
        # Test 1: Save character information
        print("\n📝 Test 1: Saving character information...")
        char_info_data = {
            'ttrpg': 'dune',
            'character_name': 'Paul Atreides - Fighter Level 1, HP: 20/20, Strength: 14',
            'character_stats': 'Son of Duke Leto. Training with Duncan Idaho. Investigating spice smuggling.'
        }
        
        char_response = client.post('/api/character-info', 
                                   data=json.dumps(char_info_data),
                                   content_type='application/json')
        
        print(f"✅ Character info saved: {char_response.status_code == 200}")
        
        # Test 2: Send a chat message that should use character information
        print("\n💬 Test 2: Sending chat message that should reference character...")
        chat_data = {
            'message': 'I want to practice my sword skills.',
            'page': 'dune',
            'character_name': 'Paul Atreides - Fighter Level 1, HP: 20/20, Strength: 14',
            'character_stats': 'Son of Duke Leto. Training with Duncan Idaho. Investigating spice smuggling.'
        }
        
        chat_response = client.post('/chat',
                                   data=json.dumps(chat_data),
                                   content_type='application/json')
        
        if chat_response.status_code == 200:
            response_data = json.loads(chat_response.data)
            ai_response = response_data.get('response', '')
            print(f"✅ Chat response received: {len(ai_response)} characters")
            print(f"📄 AI Response preview: {ai_response[:150]}...")
            
            # Check if the AI response mentions the character by name
            mentions_character = 'Paul' in ai_response or 'Duncan' in ai_response
            print(f"✅ AI uses character context: {mentions_character}")
            
            # Check if AI updated character info
            has_updates = '*[AI updated:' in ai_response
            print(f"✅ AI made updates: {has_updates}")
            
        else:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(f"Error: {chat_response.data}")
        
        # Test 3: Test character update suggestion
        print("\n⚔️ Test 3: Sending combat scenario to trigger updates...")
        combat_data = {
            'message': 'I attack the Harkonnen soldier with my sword.',
            'page': 'dune',
            'character_name': 'Paul Atreides - Fighter Level 1, HP: 20/20, Strength: 14',
            'character_stats': 'Son of Duke Leto. Training with Duncan Idaho. Investigating spice smuggling.'
        }
        
        combat_response = client.post('/chat',
                                     data=json.dumps(combat_data),
                                     content_type='application/json')
        
        if combat_response.status_code == 200:
            response_data = json.loads(combat_response.data)
            ai_response = response_data.get('response', '')
            print(f"✅ Combat response received: {len(ai_response)} characters")
            
            # Check if AI updated character after combat
            has_updates = '*[AI updated:' in ai_response
            print(f"✅ AI updated character after combat: {has_updates}")
            
            if has_updates:
                print("🎯 AI is proactively managing character information!")
            else:
                print("⚠️ AI should be more proactive in updating character info after significant events")
        
        # Test 4: Verify character info retrieval
        print("\n📖 Test 4: Retrieving saved character information...")
        get_response = client.get('/api/character-info?ttrpg=dune')
        
        if get_response.status_code == 200:
            char_data = json.loads(get_response.data)
            print(f"✅ Character info retrieved successfully")
            print(f"📝 Character Name: {char_data.get('character_name', 'None')[:50]}...")
            print(f"📝 Character Stats: {char_data.get('character_stats', 'None')[:50]}...")
        else:
            print(f"❌ Failed to retrieve character info: {get_response.status_code}")

def test_character_creation_flow():
    """Test that the AI helps with character creation proactively"""
    print("\n\n🎭 Testing Character Creation Flow...")
    
    with app.test_client() as client:
        # Login
        client.post('/login', data={'username': 'Demerzel', 'password': 'Seraphine'})
        
        # Test starting a new campaign without character
        print("\n🆕 Test: Starting new campaign without character...")
        new_campaign_data = {
            'message': 'I want to start a new Dune campaign.',
            'page': 'dune',
            'character_name': '',
            'character_stats': ''
        }
        
        response = client.post('/chat',
                              data=json.dumps(new_campaign_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            response_data = json.loads(response.data)
            ai_response = response_data.get('response', '')
            
            # Check if AI proactively offers character creation help
            offers_help = any(phrase in ai_response.lower() for phrase in [
                'character', 'create', 'guide', 'process', 'help'
            ])
            print(f"✅ AI offers character creation help: {offers_help}")
            print(f"📄 Response: {ai_response[:200]}...")
        else:
            print(f"❌ New campaign request failed: {response.status_code}")

if __name__ == '__main__':
    print("🧪 Starting Character Textbox Functionality Tests...")
    print("=" * 60)
    
    test_character_info_processing()
    test_character_creation_flow()
    
    print("\n" + "=" * 60)
    print("✅ Character textbox functionality tests completed!")
    print("\nKey improvements made:")
    print("- Enhanced character management instructions for AI")
    print("- Improved update detection and parsing")
    print("- More proactive character creation and update suggestions")
    print("- Better integration between Character Information and Notes")
