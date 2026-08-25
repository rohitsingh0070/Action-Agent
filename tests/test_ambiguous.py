def test_ambiguous_command(client):
    """
    Mandatory Test 3: Ambiguous Command
    Prompt: 'notify security if the front-gate camera goes offline'
    Expected: UNSUPPORTED parsed safely, executed=False.
    """
    payload = {
        "text": "notify security if the front-gate camera goes offline"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["understood_as"]["type"] == "UNSUPPORTED"
    assert data["executed"] is False
    assert "reason" in data["understood_as"] or "message" in data
