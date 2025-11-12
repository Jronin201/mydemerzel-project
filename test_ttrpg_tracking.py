#!/usr/bin/env python3
"""
Test for TTRPG tracking functionality
"""
import json
import os
import tempfile
from unittest.mock import patch
from app import app
import ai_client

def fake_ai_result(text="I understand you're playing Dune!", model="gpt-5"):
    return {
        "output_text": text,
        "model": model,
        "used_fallback": False,
        "id": "resp_ttrpg",
        "usage": {"input_tokens": 10, "output_tokens": 12},
    }


def login(client):
    return client.post(
        "/login",
        data={"username": "Demerzel", "password": "Seraphine"},
        follow_redirects=True,
    )


def test_ttrpg_api_endpoints():
    """Test the new TTRPG API endpoints"""
    with app.test_client() as client:
        login(client)
        
        # Test GET current TTRPG
        resp = client.get("/api/current-ttrpg")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "current_ttrpg" in data
        assert "character_info" in data
        
        # Test POST update TTRPG
        update_data = {
            "ttrpg": "dune",
            "character_name": "Paul Atreides",
            "character_stats": "Strength: 15, Dexterity: 18, Intelligence: 20"
        }
        resp = client.post("/api/current-ttrpg", json=update_data)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["current_ttrpg"] == "dune"
        assert data["character_info"]["name"] == "Paul Atreides"
        assert data["character_info"]["stats"] == "Strength: 15, Dexterity: 18, Intelligence: 20"
        
        # Verify the update persisted
        resp = client.get("/api/current-ttrpg")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["current_ttrpg"] == "dune"
        assert data["character_info"]["name"] == "Paul Atreides"


def test_universal_chatbot_page():
    """Test the new universal chatbot page with TTRPG parameters"""
    with app.test_client() as client:
        login(client)
        
    # Test universal chatbot page with TTRPG parameter
    resp = client.get("/ttrpg-chatbot?ttrpg=the-witcher")
    assert resp.status_code == 200
    assert b"The Witcher" in resp.data

    # Test without parameter (should default to general)
    resp = client.get("/ttrpg-chatbot")
    assert resp.status_code == 200


def test_legacy_redirects():
    """Test that legacy routes redirect to the universal chatbot"""
    with app.test_client() as client:
        login(client)
        
        # Test legacy routes redirect properly
        legacy_routes = ["/the-witcher", "/the-one-ring", "/dune", "/call-of-cthulhu", "/master-template"]
        for route in legacy_routes:
            resp = client.get(route)
            assert resp.status_code == 302  # Redirect
            assert "/ttrpg-chatbot" in resp.location


def test_chat_with_ttrpg_context():
    """Test that chat requests include TTRPG and character context"""
    with patch("app.save_messages_to_file"), patch(
        "app.summarize_messages",
        return_value=[{"role": "system", "content": "summary"}],
    ), patch("ai_client.request") as mock_req:
        def _side_effect(messages):
            # Simulate ai_client's internal storage of kwargs for inspection
            setattr(ai_client, "_last_ai_kwargs", {
                "input": [
                    {"role": m["role"], "content": [{"type": "input_text", "text": m["content"]}]} for m in messages
                ]
            })
            return fake_ai_result()
        mock_req.side_effect = _side_effect
        with app.test_client() as client:
            login(client)
            
            # First, set up a TTRPG context
            client.post("/api/current-ttrpg", json={
                "ttrpg": "dune",
                "character_name": "Duncan Idaho",
                "character_stats": "Combat: 20, Politics: 15"
            })
            
            # Now send a chat message
            resp = client.post("/chat", json={
                "message": "Tell me about the spice",
                "page": "dune",
                "character_name": "Duncan Idaho",
                "character_stats": "Combat: 20, Politics: 15"
            })
            
            assert resp.status_code == 200
            data = resp.get_json()
            assert "message" in data
            # Inspect last AI call constructed parts
            last = getattr(ai_client, "_last_ai_kwargs", {})
            parts = last.get("input", [])
            system_message = parts[0]["content"][0]["text"] if parts else ""
            assert "Dune" in system_message
            assert "Duncan Idaho" in system_message
            assert "Combat: 20, Politics: 15" in system_message


def test_invalid_json_to_api():
    """Test that invalid JSON to API endpoints is handled gracefully"""
    with app.test_client() as client:
        login(client)
        
        # Test with invalid JSON
        resp = client.post("/api/current-ttrpg", data="invalid json", 
                          content_type="application/json")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data


if __name__ == "__main__":
    test_ttrpg_api_endpoints()
    test_universal_chatbot_page()
    test_legacy_redirects()
    test_chat_with_ttrpg_context()
    test_invalid_json_to_api()
    print("✅ All TTRPG tracking tests passed!")
