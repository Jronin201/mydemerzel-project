#!/usr/bin/env python3
import requests
import json

def test_character_injury_update():
    """Test if AI updates character information during combat injury scenario"""
    
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'I draw my sword to fight the orc, but I stumble and get badly wounded in the leg during the battle.',
        'page': 'the-one-ring',
        'character_name': 'Gandric the Brave - Level 3 Ranger, HP: 25/25',
        'character_stats': 'Currently investigating strange happenings near Bree. Spoke with Boromir about potential spy network.'
    })
    
    if response.status_code == 200:
        data = response.json()
        print('AI Response:')
        print(data['response'])
        print()
        
        # Check if the response mentions character updates
        if '*[AI updated:' in data['response']:
            print('✅ AI proactively updated character information!')
        else:
            print('⚠️  AI did not update character information automatically')
            
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)

def test_character_level_up():
    """Test if AI updates character information when player gains experience"""
    
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'After defeating the orc leader, I feel like I have gained enough experience to level up. I want to advance to Level 4.',
        'page': 'the-one-ring',
        'character_name': 'Gandric the Brave - Level 3 Ranger, HP: 20/25 (wounded leg)',
        'character_stats': 'Currently investigating strange happenings near Bree. Recently fought orcs and was injured.'
    })
    
    if response.status_code == 200:
        data = response.json()
        print('AI Response (Level Up Test):')
        print(data['response'])
        print()
        
        # Check if the response mentions character updates
        if '*[AI updated:' in data['response']:
            print('✅ AI proactively updated character information for level up!')
        else:
            print('⚠️  AI did not update character information for level up')
            
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)

if __name__ == "__main__":
    print("Testing AI Character Information Management")
    print("="*50)
    test_character_injury_update()
    print()
    test_character_level_up()
