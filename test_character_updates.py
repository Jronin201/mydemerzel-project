#!/usr/bin/env python3
"""
Direct test of character update functionality with explicit scenarios
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import app

def test_explicit_character_updates():
    """Test explicit scenarios that should trigger character updates"""
    print("🧪 Testing Explicit Character Update Scenarios...")
    
    with app.test_client() as client:
        # Login
        client.post('/login', data={'username': 'Demerzel', 'password': 'Seraphine'})
        
        # Scenario 1: Direct request to update character
        print("\n📝 Test 1: Direct request to update character...")
        update_request_data = {
            'message': 'I gained a level! Update my character to show I am now Level 2 and learned a new skill: Advanced Swordplay.',
            'page': 'the-one-ring',
            'character_name': 'Aragorn - Ranger Level 1, Hope: 15, Shadow: 2',
            'character_stats': 'Strider. Seeks to protect the innocent. Skilled tracker.'
        }
        
        update_response = client.post('/chat',
                                     data=json.dumps(update_request_data),
                                     content_type='application/json')
        
        if update_response.status_code == 200:
            response_data = json.loads(update_response.data)
            ai_response = response_data.get('response', '')
            print(f"📄 AI Response: {ai_response}")
            
            has_updates = '*[AI updated:' in ai_response
            print(f"✅ AI updated character: {has_updates}")
            
            if has_updates:
                print("🎯 SUCCESS: AI can update character when directly requested!")
            else:
                print("⚠️ AI did not update character despite direct request")
        
        # Scenario 2: Subtle scenario that should trigger updates
        print("\n⚔️ Test 2: Combat with injury that should update character...")
        injury_data = {
            'message': 'The orc\'s blade cuts deep into my arm. I\'m wounded but still fighting.',
            'page': 'the-one-ring',
            'character_name': 'Aragorn - Ranger Level 2, Hope: 15, Shadow: 2',
            'character_stats': 'Strider. Seeks to protect the innocent. Advanced Swordplay skill.'
        }
        
        injury_response = client.post('/chat',
                                     data=json.dumps(injury_data),
                                     content_type='application/json')
        
        if injury_response.status_code == 200:
            response_data = json.loads(injury_response.data)
            ai_response = response_data.get('response', '')
            print(f"📄 AI Response: {ai_response}")
            
            has_updates = '*[AI updated:' in ai_response
            print(f"✅ AI updated character for injury: {has_updates}")
        
        # Scenario 3: Story progression
        print("\n📖 Test 3: Important story event...")
        story_data = {
            'message': 'I discover that Boromir is actually a spy for Saruman! This is shocking news.',
            'page': 'the-one-ring',
            'character_name': 'Aragorn - Ranger Level 2, Hope: 15, Shadow: 2, Wounded',
            'character_stats': 'Strider. Seeks to protect the innocent. Advanced Swordplay skill.'
        }
        
        story_response = client.post('/chat',
                                    data=json.dumps(story_data),
                                    content_type='application/json')
        
        if story_response.status_code == 200:
            response_data = json.loads(story_response.data)
            ai_response = response_data.get('response', '')
            print(f"📄 AI Response: {ai_response}")
            
            has_updates = '*[AI updated:' in ai_response
            mentions_boromir = 'Boromir' in ai_response or 'spy' in ai_response.lower()
            print(f"✅ AI updated notes for story: {has_updates}")
            print(f"✅ AI acknowledges story event: {mentions_boromir}")
        
        # Test character info retrieval after updates
        print("\n📖 Checking final character state...")
        get_response = client.get('/api/character-info?ttrpg=the-one-ring')
        
        if get_response.status_code == 200:
            char_data = json.loads(get_response.data)
            print(f"Final Character Name: {char_data.get('character_name', 'None')}")
            print(f"Final Character Stats: {char_data.get('character_stats', 'None')}")

if __name__ == '__main__':
    test_explicit_character_updates()
