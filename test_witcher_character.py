#!/usr/bin/env python3
"""
Test focused on The Witcher to avoid Dune's campaign manager interference
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

def test_witcher_character_functionality():
    """Test character functionality with The Witcher (no campaign manager interference)"""
    print("🧪 Testing The Witcher Character Information Processing...")
    
    with app.test_client() as client:
        # Login
        client.post('/login', data={'username': 'Demerzel', 'password': 'Seraphine'})

        # Save character information for The Witcher
        char_info_data = {
            'ttrpg': 'the-witcher',
            'character_name': 'Geralt of Rivia – Witcher, Vitality: 42, Toxicity: 0',
            'character_stats': 'Mutagenically enhanced monster slayer. Carries steel & silver blades, Signs training, alchemy toolkit.'
        }
        
        char_response = client.post('/api/character-info', 
                                   data=json.dumps(char_info_data),
                                   content_type='application/json')
        
        print(f"✅ Character info saved: {char_response.status_code == 200}")
        
        # Test character-aware chat
        chat_data = {
            'message': 'I want to explore the foggy swamps near Novigrad.',
            'page': 'the-witcher',
            'character_name': 'Geralt of Rivia – Witcher, Vitality: 42, Toxicity: 0',
            'character_stats': 'Mutagenically enhanced monster slayer. Carries steel & silver blades, Signs training, alchemy toolkit.'
        }
        
        chat_response = client.post('/chat',
                                   data=json.dumps(chat_data),
                                   content_type='application/json')
        
        if chat_response.status_code == 200:
            response_data = json.loads(chat_response.data)
            ai_response = response_data.get('response', '')
            print(f"✅ Chat response received: {len(ai_response)} characters")
            print(f"📄 AI Response: {ai_response}")
            
            # Check if AI uses character context
            mentions_character = 'Geralt' in ai_response or 'witcher' in ai_response.lower() or 'monster' in ai_response.lower()
            print(f"✅ AI uses character context: {mentions_character}")
            
            # Check for updates
            has_updates = '*[AI updated:' in ai_response
            print(f"📝 AI made updates: {has_updates}")
            
        else:
            print(f"❌ Chat failed: {chat_response.status_code} - {chat_response.data}")
        
        # Test combat scenario
        print("\n⚔️ Testing combat scenario for proactive updates...")
        combat_data = {
            'message': 'A pack of drowners leaps from the water! I ready my silver sword and cast Igni.',
            'page': 'the-witcher',
            'character_name': 'Geralt of Rivia – Witcher, Vitality: 42, Toxicity: 0',
            'character_stats': 'Mutagenically enhanced monster slayer. Carries steel & silver blades, Signs training, alchemy toolkit.'
        }
        
        combat_response = client.post('/chat',
                                     data=json.dumps(combat_data),
                                     content_type='application/json')
        
        if combat_response.status_code == 200:
            response_data = json.loads(combat_response.data)
            ai_response = response_data.get('response', '')
            print(f"📄 Combat Response: {ai_response}")
            
            has_updates = '*[AI updated:' in ai_response
            print(f"✅ AI updated character after combat: {has_updates}")
            
            if not has_updates:
                print("⚠️ Expected AI to update character (Hope/Shadow) after dangerous encounter")
        
        # Test character creation scenario
        print("\n🎭 Testing character creation suggestion...")
        creation_data = {
            'message': 'I want to create a new witcher from the School of the Cat.',
            'page': 'the-witcher',
            'character_name': '',
            'character_stats': ''
        }
        
        creation_response = client.post('/chat',
                                       data=json.dumps(creation_data),
                                       content_type='application/json')
        
        if creation_response.status_code == 200:
            response_data = json.loads(creation_response.data)
            ai_response = response_data.get('response', '')
            print(f"📄 Creation Response: {ai_response}")
            
            # Check if AI offers to help with character creation
            offers_help = any(word in ai_response.lower() for word in ['help', 'create', 'guide', 'character'])
            print(f"✅ AI offers character creation help: {offers_help}")

if __name__ == '__main__':
    test_witcher_character_functionality()
