def test_out_of_scope_unsupported(client):
    """
    Mandatory Test 4: Out of Scope Command
    Prompt: 'turn off all the lights in building 7'
    Expected: UNSUPPORTED parsed, executed=False, reason explains lighting control is outside monitoring scope.
    """
    payload = {
        "text": "turn off all the lights in building 7"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "unsupported"
    assert data["executed"] is False
    assert data["understood_as"]["type"] == "UNSUPPORTED"
    assert "lighting" in data["understood_as"]["reason"].lower() or "outside" in data["understood_as"]["reason"].lower()
