#!/usr/bin/env python3
import requests
import json

def test_character_injury_update():
    """Test if AI updates character information during combat injury scenario"""
    
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'I ignite Igni to fend off a wyvern, but its talons tear across my ribs and leave me bleeding.',
        'page': 'the-witcher',
        'character_name': 'Geralt of Rivia - Witcher Rank 2, Vitality: 34/42',
        'character_stats': 'Currently contracted near Novigrad. Carrying specter oil and thunderbolt potion. Tracking Nilfgaardian activity.'
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
        'message': 'After slaying the wyvern and securing proof, I feel ready to advance to Witcher Rank 3. Note my new precision training.',
        'page': 'the-witcher',
        'character_name': 'Geralt of Rivia - Witcher Rank 2, Vitality: 28/42 (bleeding)',
        'character_stats': 'Contract near Novigrad. Carrying specter oil, thunderbolt potion, and fresh wyvern trophy. Shoulder heavily bandaged.'
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
