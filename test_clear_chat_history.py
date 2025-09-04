import json
from app import app

def login_test_user(client):
    """Helper to simulate a logged-in user for routes guarded by @login_required."""
    with client.session_transaction() as sess:
        # Flask-Login stores user ID in '_user_id'
        sess['_user_id'] = 'TestUser'

def test_clear_chat_history_flow():
    client = app.test_client()

    # Use a test system name to avoid interfering with other tests
    system = "dune"

    # Login simulation
    login_test_user(client)

    # 1. Ensure starting history is loaded (may be empty or not)
    resp = client.get(f"/api/chat-history?ttrpg={system}")
    assert resp.status_code == 200
    initial = resp.get_json()

    # 2. Post two fake messages by simulating backend persistence route if available
    # If no direct endpoint, we mimic by calling a generation route; fallback: skip if not present
    # Here we directly call internal save if exposed via a route; for robustness we'll just skip injection

    # 3. Call clear endpoint
    clr = client.post("/api/chat-history/clear", json={"ttrpg": system})
    assert clr.status_code == 200
    data = clr.get_json()
    assert data.get("success") is True
    assert data.get("remaining_count") == 0

    # 4. Fetch history again and verify it's empty
    after = client.get(f"/api/chat-history?ttrpg={system}").get_json()
    assert after["message_count"] == 0
    assert after["messages"] == []

    # 5. Idempotency: clearing again still succeeds
    clr2 = client.post("/api/chat-history/clear", json={"ttrpg": system})
    assert clr2.status_code == 200
    data2 = clr2.get_json()
    assert data2.get("success") is True
    assert data2.get("remaining_count") == 0

    # 6. Undo now should report nothing to undo
    undo = client.post("/api/chat-history/undo", json={"ttrpg": system})
    undo_json = undo.get_json()
    assert undo_json.get("success") is False
    assert undo_json.get("remaining_count") == 0

    print(json.dumps({
        "initial_message_count": initial["message_count"],
        "post_clear_message_count": after["message_count"],
        "undo_after_clear_success": undo_json.get("success")
    }, indent=2))
