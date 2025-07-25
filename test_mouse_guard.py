#!/usr/bin/env python3
import requests
import json

def test_mouse_guard_chatbot():
    """Test Mouse Guard chatbot setup and greeting"""
    
    # Test the chatbot response for Mouse Guard
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'Hello, I want to start a new Mouse Guard campaign.',
        'page': 'mouse-guard',
        'character_name': '',
        'character_stats': ''
    })
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Mouse Guard Chatbot Response:')
        print(data['response'])
        print()
        
        # Check if the response mentions Mouse Guard specifically
        if 'mouse guard' in data['response'].lower() or 'mouse territories' in data['response'].lower():
            print('✅ AI correctly identifies Mouse Guard system!')
        else:
            print('⚠️  AI response does not clearly indicate Mouse Guard awareness')
            
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)

def test_mouse_guard_greeting():
    """Test the initial greeting for Mouse Guard"""
    
    # Get initial greeting (empty chat history)
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'test',
        'page': 'mouse-guard',
        'character_name': '',
        'character_stats': ''
    })
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Mouse Guard Initial Greeting:')
        print(data['response'])
        print()
        
        # Check if the greeting is Mouse Guard specific
        if 'mouse territories' in data['response'].lower():
            print('✅ Greeting correctly mentions Mouse Territories!')
        else:
            print('⚠️  Greeting does not mention Mouse Guard specifically')
            
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)

if __name__ == "__main__":
    print("Testing Mouse Guard Chatbot Setup")
    print("="*50)
    test_mouse_guard_greeting()
    print()
    test_mouse_guard_chatbot()
