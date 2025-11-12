#!/usr/bin/env python3
"""
Test for per-user, per-TTRPG chat history functionality
"""
import os
import shutil
import json
import types
from unittest.mock import patch
import types as _types
import ai_client
from app import app


def fake_ai_result(text="Hello from OpenAI", model="gpt-5"):
    return {
        "output_text": text,
        "model": model,
        "used_fallback": False,
        "id": "resp_test",
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


def login(client):
    return client.post(
        "/login",
        data={"username": "Demerzel", "password": "Seraphine"},
        follow_redirects=True,
    )


def clean_test_data():
    """Clean up test chat history data"""
    if os.path.exists("chat_histories"):
        shutil.rmtree("chat_histories")


def test_per_user_chat_history():
    """Test that each user gets their own chat history"""
    clean_test_data()
    
    
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result("Hello, Demerzel!")):
        
        with app.test_client() as client:
            login(client)
            
            # Send a message in the dune TTRPG
            resp = client.post("/chat", json={
                "message": "I want to explore Arrakis",
                "page": "dune",
                "character_name": "Paul Atreides",
                "character_stats": "Prescience: High"
            })
            
            assert resp.status_code == 200
            
            # Check chat history API
            resp = client.get("/api/chat-history?ttrpg=dune")
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["username"] == "Demerzel"
            assert data["ttrpg_system"] == "dune"
            assert data["message_count"] == 2  # user + assistant
            assert any(msg["content"] == "I want to explore Arrakis" for msg in data["messages"])


def test_separate_ttrpg_histories():
    """Test that different TTRPG systems have separate chat histories"""
    clean_test_data()
    
    
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result("AI response")):
        
        with app.test_client() as client:
            login(client)
            
            # Send message in Dune TTRPG
            client.post("/chat", json={
                "message": "Tell me about spice",
                "page": "dune"
            })
            
            # Send message in The Witcher TTRPG
            client.post("/chat", json={
                "message": "Tell me about witcher contracts",
                "page": "the-witcher"
            })
            
            # Check Dune history
            resp = client.get("/api/chat-history?ttrpg=dune")
            dune_data = resp.get_json()
            assert any(msg["content"] == "Tell me about spice" for msg in dune_data["messages"])
            assert not any("witcher" in msg["content"].lower() for msg in dune_data["messages"])
            
            # Check The Witcher history
            resp = client.get("/api/chat-history?ttrpg=the-witcher")
            witcher_data = resp.get_json()
            assert any("witcher contracts" in msg["content"].lower() for msg in witcher_data["messages"])
            assert not any("spice" in msg["content"].lower() for msg in witcher_data["messages"])


def test_chat_sessions_api():
    """Test the chat sessions API that lists all user sessions"""
    clean_test_data()
    
    
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result("AI response")):
        
        with app.test_client() as client:
            login(client)
            
            # Create chat histories for multiple TTRPGs
            client.post("/chat", json={"message": "Dune message", "page": "dune"})
            client.post("/chat", json={"message": "Witcher message", "page": "the-witcher"})
            client.post("/chat", json={"message": "Zweihander message", "page": "zweihander"})
            
            # Get all sessions
            resp = client.get("/api/chat-sessions")
            assert resp.status_code == 200
            data = resp.get_json()
            
            assert data["username"] == "Demerzel"
            assert len(data["sessions"]) == 3
            
            session_names = [session["ttrpg_system"] for session in data["sessions"]]
            assert "dune" in session_names
            assert "the-witcher" in session_names
            assert "zweihander" in session_names


def test_persistent_chat_history():
    """Test that chat history persists across requests"""
    clean_test_data()
    
    
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result("AI response")):
        
        with app.test_client() as client:
            login(client)
            
            # Send first message
            client.post("/chat", json={
                "message": "First message",
                "page": "dune"
            })
            
            # Send second message  
            client.post("/chat", json={
                "message": "Second message",
                "page": "dune"
            })
            
            # Check that both messages are in history
            resp = client.get("/api/chat-history?ttrpg=dune")
            data = resp.get_json()
            
            assert data["message_count"] == 4  # 2 user + 2 assistant
            messages = data["messages"]
            assert any(msg["content"] == "First message" for msg in messages)
            assert any(msg["content"] == "Second message" for msg in messages)


def test_character_info_persistence():
    """Test that character info is saved with TTRPG context"""
    clean_test_data()
    
    
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result("AI response")) as mock_req:
        
        with app.test_client() as client:
            login(client)
            
            # Send message with character info
            client.post("/chat", json={
                "message": "I explore the desert",
                "page": "dune",
                "character_name": "Duncan Idaho",
                "character_stats": "Swordsmaster: Expert, Loyalty: House Atreides"
            })
            
            # Verify character info persisted to storage
            from user_character_info import load_user_character_info
            stored = load_user_character_info("Demerzel", "dune")
            assert "Duncan Idaho" in stored.get("character_name", "")
            assert "Swordsmaster: Expert" in stored.get("character_stats", "")


if __name__ == "__main__":
    try:
        test_per_user_chat_history()
        test_separate_ttrpg_histories()
        test_chat_sessions_api()
        test_persistent_chat_history()
        test_character_info_persistence()
        print("✅ All per-user, per-TTRPG chat history tests passed!")
    finally:
        clean_test_data()  # Clean up after tests
