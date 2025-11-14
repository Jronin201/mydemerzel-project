from unittest.mock import patch
from app import app
import ai_client

def fake_ai_result(text="test reply", model="gpt-5.1"):
    return {
        "output_text": text,
        "model": model,
        "used_fallback": False,
        "id": "resp_full_app",
        "usage": {"input_tokens": 5, "output_tokens": 5},
    }


def login(client):
    return client.post(
        "/login",
        data={"username": "Demerzel", "password": "Seraphine"},
        follow_redirects=True,
    )


def test_root_page():
    with app.test_client() as client:
        login(client)
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Demerzel" in resp.data


def test_static_pages():
    # These legacy routes now redirect to universal chatbot (302 expected)
    paths = ["/the-witcher", "/the-one-ring", "/call-of-cthulhu", "/master-template"]
    with app.test_client() as client:
        login(client)
        for path in paths:
            resp = client.get(path)
            assert resp.status_code in (200, 302)


def test_chat_success():
    with patch("app.save_messages_to_file"), patch(
        "app.summarize_messages",
        return_value=[{"role": "system", "content": "summary"}],
    ), patch("ai_client.request", return_value=fake_ai_result("test reply")) as mock_req:
        with app.test_client() as client:
            login(client)
            resp = client.post("/chat", json={
                "message": "Describe Arrakis environment details.",
                "page": "dune",
                "character_name": "Paul Atreides",
                "character_stats": "Prescience: High"
            })
            assert resp.status_code == 200
            data = resp.get_json()
            # When no page/character info and first message 'hello', system returns greeting not AI call
            # So either greeting (no model metadata) or AI response with footer
            assert "message" in data
            assert mock_req.called


def test_chat_empty_input():
    with app.test_client() as client:
        resp = client.post("/chat", json={"message": "   "})
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Empty input"}
