#!/usr/bin/env python3
"""
Test script for optimized embedding search.
Run this after starting your Flask application.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_embedding_search():
    """Test the optimized embedding search functionality."""
    print("🧪 TESTING OPTIMIZED EMBEDDING SEARCH")
    print("=" * 50)
    
    # Login first
    session = requests.Session()
    login_data = {"username": "Demerzel", "password": "Seraphine"}
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code != 200:
            print("❌ Login failed - make sure Flask app is running")
            return False
        print("✅ Logged in successfully")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
        return False
    
    # Test queries for different TTRPG systems
    test_queries = {
        "dune": [
            "How do I mine spice on Arrakis?",
            "What are the powers of the Bene Gesserit?",
            "Tell me about House Atreides"
        ],
        "the-one-ring": [
            "How do I brew and use potions as a witcher?",
            "How does a witcher track a nocturnal flying monster?",
            "How does a witcher negotiate a monster contract?"
        ]
    }
    
    for ttrpg, queries in test_queries.items():
        print(f"\n🎮 Testing {ttrpg.upper()} system...")
        
        for query in queries:
            chat_data = {
                "message": query,
                "page": ttrpg
            }
            
            try:
                response = session.post(
                    f"{BASE_URL}/chat",
                    json=chat_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    print(f"   ✅ Query: {query}")
                    print(f"      Response length: {len(ai_response)} chars")
                    print(f"      Preview: {ai_response[:100]}...")
                else:
                    print(f"   ❌ Query failed: {query} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ Error testing query '{query}': {e}")
    
    print("\n✅ Testing complete!")
    print("\n💡 Tips to verify improvements:")
    print("   • Responses should be more relevant and specific")
    print("   • Check Flask console for DEBUG messages about embedding search")
    print("   • Multiple reference sources should be used (check console logs)")

if __name__ == "__main__":
    test_embedding_search()
