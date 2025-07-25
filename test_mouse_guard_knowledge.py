#!/usr/bin/env python3
import requests
import json

def test_mouse_guard_knowledge():
    """Test Mouse Guard specific knowledge and context"""
    
    # Test Mouse Guard specific concepts
    response = requests.post('http://localhost:5000/chat', json={
        'message': 'Tell me about Lockhaven and the Mouse Guard patrol duties.',
        'page': 'mouse-guard',
        'character_name': 'Bramble - Tenderpaw',
        'character_stats': 'New recruit to the Mouse Guard, eager to prove herself on patrol duties.'
    })
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Mouse Guard Knowledge Test:')
        print(data['response'])
        print()
        
        # Check for Mouse Guard specific terms
        response_lower = data['response'].lower()
        mg_terms = ['lockhaven', 'patrol', 'guard', 'mouse', 'tenderpaw', 'territories']
        found_terms = [term for term in mg_terms if term in response_lower]
        
        if len(found_terms) >= 3:
            print(f'✅ AI demonstrates Mouse Guard knowledge! Found terms: {", ".join(found_terms)}')
        else:
            print(f'⚠️  Limited Mouse Guard knowledge. Found terms: {", ".join(found_terms)}')
            
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)

if __name__ == "__main__":
    print("Testing Mouse Guard Knowledge and Context")
    print("="*50)
    test_mouse_guard_knowledge()
