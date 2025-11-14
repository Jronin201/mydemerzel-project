#!/usr/bin/env python3
"""
End-to-end integration test for the complete TTRPG chat history system
This demonstrates the full workflow from login to chat persistence
"""
from unittest.mock import patch
from app import app
import ai_client

def fake_ai_result(text="AI: I understand you're playing Dune!", model="gpt-5.1"):
    return {
        "output_text": text,
        "model": model,
        "used_fallback": False,
        "id": "resp_integration",
        "usage": {"input_tokens": 10, "output_tokens": 12},
    }


def login(client):
    return client.post(
        "/login",
        data={"username": "Demerzel", "password": "Seraphine"},
        follow_redirects=True,
    )


def simulate_full_user_journey():
    """Simulate a complete user journey through the TTRPG system"""
    
    # Mock app.messages for backward compatibility
    with patch("app.summarize_messages", return_value=[{"role": "system", "content": "summary"}]), \
         patch("ai_client.request", return_value=fake_ai_result()):
        
        with app.test_client() as client:
            print("1. User logs in...")
            login_resp = login(client)
            assert login_resp.status_code == 200
            print("   ✅ Login successful")
            
            print("\n2. User visits main page and selects Dune...")
            main_resp = client.get("/")
            assert main_resp.status_code == 200
            print("   ✅ Main page loaded")
            
            print("\n3. User navigates to Dune chatbot (via redirect)...")
            dune_resp = client.get("/dune")
            assert dune_resp.status_code == 302  # Redirect to universal chatbot
            print("   ✅ Legacy route redirects correctly")
            
            print("\n4. User loads universal chatbot for Dune...")
            chatbot_resp = client.get("/ttrpg-chatbot?ttrpg=dune")
            assert chatbot_resp.status_code == 200
            assert b"Dune" in chatbot_resp.data
            print("   ✅ Universal chatbot loaded with Dune configuration")
            
            print("\n5. User checks for existing chat history (should be empty)...")
            history_resp = client.get("/api/chat-history?ttrpg=dune")
            assert history_resp.status_code == 200
            initial_data = history_resp.get_json()
            assert initial_data["message_count"] == 0
            print("   ✅ No existing chat history found")
            
            print("\n6. User sends first chat message with character info...")
            chat_resp = client.post("/chat", json={
                "message": "I want to explore Arrakis and learn about the spice",
                "page": "dune",
                "character_name": "Paul Atreides",
                "character_stats": "Prescience: High, Leadership: Expert, Bene Gesserit Training: Advanced"
            })
            assert chat_resp.status_code == 200
            response_data = chat_resp.get_json()
            assert "message" in response_data
            print("   ✅ First message sent and AI responded")
            
            print("\n7. Verify TTRPG and character info was updated...")
            ttrpg_resp = client.get("/api/current-ttrpg")
            ttrpg_data = ttrpg_resp.get_json()
            assert ttrpg_data["current_ttrpg"] == "dune"
            assert ttrpg_data["character_info"]["name"] == "Paul Atreides"
            print("   ✅ TTRPG and character info correctly updated")
            
            print("\n8. User sends second message...")
            chat_resp2 = client.post("/chat", json={
                "message": "Tell me about the Fremen culture",
                "page": "dune"
            })
            assert chat_resp2.status_code == 200
            print("   ✅ Second message sent")
            
            print("\n9. Check that chat history now contains both messages...")
            history_resp2 = client.get("/api/chat-history?ttrpg=dune")
            history_data = history_resp2.get_json()
            assert history_data["message_count"] == 4  # 2 user + 2 assistant
            messages = history_data["messages"]
            assert any("explore Arrakis" in msg["content"] for msg in messages)
            assert any("Fremen culture" in msg["content"] for msg in messages)
            print("   ✅ Chat history contains both messages")
            
            print("\n10. User switches to The Witcher TTRPG...")
            tor_resp = client.get("/ttrpg-chatbot?ttrpg=the-witcher")
            assert tor_resp.status_code == 200
            print("   ✅ Switched to The Witcher TTRPG")
            
            print("\n11. Send message in The Witcher system...")
            tor_chat_resp = client.post("/chat", json={
                "message": "I will take a contract to hunt the leshen near Novigrad",
                "page": "the-witcher",
                "character_name": "Geralt of Rivia", 
                "character_stats": "School of the Wolf witcher, master swordsman, signs adept"
            })
            assert tor_chat_resp.status_code == 200
            print("   ✅ Message sent in The Witcher system")
            
            print("\n12. Verify separate chat histories...")
            # Check Dune history is unchanged
            dune_history = client.get("/api/chat-history?ttrpg=dune").get_json()
            assert dune_history["message_count"] == 4
            assert not any("leshen" in msg["content"] for msg in dune_history["messages"])
            
            # Check The Witcher history has new message
            tor_history = client.get("/api/chat-history?ttrpg=the-witcher").get_json()
            assert tor_history["message_count"] == 2  # 1 user + 1 assistant
            assert any("leshen" in msg["content"] for msg in tor_history["messages"])
            print("   ✅ Chat histories are properly separated by TTRPG system")
            
            print("\n13. Check user's all chat sessions...")
            sessions_resp = client.get("/api/chat-sessions")
            sessions_data = sessions_resp.get_json()
            assert len(sessions_data["sessions"]) == 2
            session_names = [s["ttrpg_system"] for s in sessions_data["sessions"]]
            assert "dune" in session_names
            assert "the-witcher" in session_names
            print("   ✅ All user sessions listed correctly")
            
            print("\n🎉 Complete user journey test passed!")
            print("   - User authentication ✅")
            print("   - TTRPG system selection ✅") 
            print("   - Chat message persistence ✅")
            print("   - Character info tracking ✅")
            print("   - Separate histories per TTRPG ✅")
            print("   - Session management ✅")


if __name__ == "__main__":
    simulate_full_user_journey()
    print("\n✅ End-to-end integration test completed successfully!")
