import types
from unittest.mock import patch
from app import app


def fake_openai_response(content="Hello from OpenAI"):
    return types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content))]
    )


def test_root_page():
    with app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Demerzel" in resp.data


def test_static_pages():
    paths = ["/the-one-ring", "/call-of-cthulhu", "/master-template"]
    with app.test_client() as client:
        for path in paths:
            resp = client.get(path)
            assert resp.status_code == 200


def test_chat_success():
    app.messages = []
    with patch("app.save_messages_to_file"), patch(
        "app.summarize_messages",
        return_value=[{"role": "system", "content": "summary"}],
    ), patch(
        "app.client.chat.completions.create",
        return_value=fake_openai_response("test reply"),
    ) as mock_create:
        with app.test_client() as client:
            resp = client.post("/chat", json={"message": "hello"})
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["response"] == "test reply"
            mock_create.assert_called_once()


def test_chat_empty_input():
    with app.test_client() as client:
        resp = client.post("/chat", json={"message": "   "})
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Empty input"}
