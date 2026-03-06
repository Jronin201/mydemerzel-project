from io import BytesIO
import os
import json

import ai_client
import app as flask_app

app = flask_app.app


def login_test_user(client):
    with client.session_transaction() as sess:
        sess["_user_id"] = "TestUser"


def test_upload_pdf_requires_login():
    with app.test_client() as client:
        resp = client.post(
            "/api/upload-pdf",
            data={"file": (BytesIO(b"%PDF-1.4\ncontent"), "sample.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code in (302, 401)


def test_upload_pdf_rejects_non_pdf_extension():
    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/api/upload-pdf",
            data={"file": (BytesIO(b"not-pdf"), "notes.txt")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "Only PDF files" in resp.get_json()["error"]


def test_upload_pdf_rejects_invalid_header():
    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/api/upload-pdf",
            data={"file": (BytesIO(b"BAD!! not a pdf"), "bad.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "Invalid PDF" in resp.get_json()["error"]


def test_upload_pdf_rejects_oversized(monkeypatch):
    monkeypatch.setattr(flask_app, "MAX_PDF_UPLOAD_BYTES", 10, raising=False)

    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/api/upload-pdf",
            data={"file": (BytesIO(b"%PDF-1.4\n" + b"x" * 200), "big.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "File exceeds size limit" in resp.get_json()["error"]


def test_upload_pdf_success_and_temp_cleanup(monkeypatch):
    seen_paths = []

    def fake_upload_user_file(path, purpose="user_data"):
        seen_paths.append(path)
        # Temp file should exist while uploading
        assert os.path.exists(path)
        assert purpose == "user_data"
        return {"id": "file-test123", "filename": "ok.pdf", "bytes": 16, "purpose": purpose}

    monkeypatch.setattr(ai_client, "upload_user_file", fake_upload_user_file)

    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/api/upload-pdf",
            data={"file": (BytesIO(b"%PDF-1.4\nhello"), "ok.pdf")},
            content_type="multipart/form-data",
        )

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert body["file_id"] == "file-test123"
    assert seen_paths, "Expected upload helper to be called"
    # Temp file should be removed in route finally block
    assert not os.path.exists(seen_paths[0])


def test_chat_passes_file_id_to_ai_request(monkeypatch):
    captured = {}

    def fake_request(messages, **kwargs):
        captured["kwargs"] = kwargs
        return {
            "output_text": "PDF answer",
            "model": "gpt-5.3",
            "used_fallback": False,
            "id": "resp_test",
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }

    monkeypatch.setattr(ai_client, "request", fake_request)
    monkeypatch.setattr(flask_app, "save_user_chat", lambda *args, **kwargs: True, raising=False)
    monkeypatch.setattr(flask_app, "update_current_ttrpg", lambda *args, **kwargs: {}, raising=False)

    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/chat",
            json={
                "message": "What is in the PDF?",
                "page": "general",
                "file_id": "file-test123",
            },
        )

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["response"] == "PDF answer"
    assert "kwargs" in captured
    assert captured["kwargs"].get("file_ids") == ["file-test123"]


def test_chat_streaming_passes_file_id_to_ai_request_stream(monkeypatch):
    captured = {}

    def fake_request_stream(messages, **kwargs):
        captured["kwargs"] = kwargs
        yield ("delta", "Streamed PDF answer")
        yield (
            "done",
            {
                "model": "gpt-5.3",
                "id": "resp_stream_test",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    monkeypatch.setenv("OPENAI_STREAM_RESPONSES", "true")
    monkeypatch.setattr(ai_client, "request_stream", fake_request_stream)
    monkeypatch.setattr(flask_app, "save_user_chat", lambda *args, **kwargs: True, raising=False)
    monkeypatch.setattr(flask_app, "update_current_ttrpg", lambda *args, **kwargs: {}, raising=False)

    with app.test_client() as client:
        login_test_user(client)
        resp = client.post(
            "/chat",
            json={
                "message": "Use the uploaded PDF in streaming mode",
                "page": "general",
                "file_id": "file-stream123",
            },
            headers={"Accept": "text/event-stream"},
        )

    assert resp.status_code == 200
    body = b"".join(resp.response).decode("utf-8")
    done_lines = [line for line in body.splitlines() if line.startswith("data: ")]
    assert done_lines, "Expected SSE data lines in streaming response"
    # Last data payload corresponds to done metadata.
    done_payload = json.loads(done_lines[-1][6:])
    assert done_payload["model"] == "gpt-5.3"
    assert "kwargs" in captured
    assert captured["kwargs"].get("file_ids") == ["file-stream123"]
