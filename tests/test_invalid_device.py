def test_invalid_device_rejection(client):
    """
    Mandatory Test 5: Invalid Device Rejection
    Prompt: 'alert me if the reactor-core pressure exceeds 9000'
    Expected: LLM parses structured intent, but backend device registry validation catches that 'reactor-core'
    does NOT exist in registry and rejects execution (executed=False, status='validation_error').
    """
    payload = {
        "text": "alert me if the reactor-core pressure exceeds 9000"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # The LLM parser extracts reactor-core intent
    assert data["understood_as"]["type"] == "CREATE_ALERT_RULE"
    assert data["understood_as"]["device_id"] == "reactor-core"

    # Crucial: Backend validation rejects it!
    assert data["status"] == "validation_error"
    assert data["executed"] is False
    assert data["errors"] is not None
    assert any("reactor-core" in err for err in data["errors"])
