#!/usr/bin/env python3
"""
Test script to verify the updated TTRPG chatbot interface
"""
import types
from unittest.mock import patch
from app import app


def fake_openai_response(content="Hello from OpenAI"):
    return types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content))]
    )


def login(client):
    return client.post(
        "/login",
        data={"username": "Demerzel", "password": "Seraphine"},
        follow_redirects=True,
    )


def test_updated_interface():
    """Test that the updated interface loads correctly"""
    
    with app.test_client() as client:
        print("Testing updated TTRPG chatbot interface...")
        
        # Login
        login_resp = login(client)
        assert login_resp.status_code == 200
        print("✅ Login successful")
        
        # Load the universal chatbot page
        resp = client.get("/ttrpg-chatbot?ttrpg=the-witcher")
        assert resp.status_code == 200
        
        # Check that the new labels are present
        content = resp.data.decode('utf-8')
        assert "Character Information:" in content
        assert "Notes:" in content
        
        # Check that textareas are used instead of inputs
        assert 'class="styled-textarea auto-resize"' in content
        assert 'id="character-name"' in content
        assert 'id="stat-value"' in content
        
        # Check that old labels are not present
        assert "Character Name:" not in content
        assert "Character Stats:" not in content
        
        print("✅ Updated labels found")
        print("✅ Textareas with auto-resize class found")
        print("✅ Old labels removed")
        
        # Test API endpoint still works with new structure
        resp = client.get("/api/current-ttrpg")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "character_info" in data
        print("✅ API endpoint still functional")

        # Test updating character info with new structure
        resp = client.post("/api/current-ttrpg", json={
            "ttrpg": "the-witcher",
            "character_name": "Geralt of Rivia\nWitcher from Kaer Morhen",
            "character_stats": "Signs: Aard (Skilled)\nAlchemy: Oils & Decoctions Ready\nNotes: Carries silver and steel blades"
        })
        assert resp.status_code == 200
        updated_data = resp.get_json()
        assert "Geralt" in updated_data["character_info"]["name"]
        assert "silver and steel" in updated_data["character_info"]["stats"]
        print("✅ Multi-line character information saves correctly")


if __name__ == "__main__":
    test_updated_interface()
    print("\n🎉 All interface update tests passed!")
    print("📝 New features:")
    print("   • 'Character Name' → 'Character Information'")
    print("   • 'Character Stats' → 'Notes'") 
    print("   • Text inputs → Auto-resizing textareas")
    print("   • Dynamic height based on content")
    print("   • Expand on Enter, shrink on blur")
    print("   • Multi-line character information support")
