def test_valid_create_alert_rule(client):
    """
    Mandatory Test 1: Valid Alert Rule Creation
    Prompt: 'Alert me if warehouse-3 temperature stays above 40°C for more than 10 minutes'
    Expected: CREATE_ALERT_RULE parsed, executed successfully, rule appended to in-memory store & queryable via GET /rules.
    """
    payload = {
        "text": "Alert me if warehouse-3 temperature stays above 40°C for more than 10 minutes"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # Verify response structure
    assert data["status"] == "success"
    assert data["executed"] is True
    assert data["understood_as"]["type"] == "CREATE_ALERT_RULE"
    assert data["understood_as"]["device_id"] == "warehouse-3"
    assert data["understood_as"]["metric"] == "temperature"
    assert data["understood_as"]["condition"] == "ABOVE"
    assert data["understood_as"]["threshold"] == 40.0
    assert data["understood_as"]["duration_minutes"] == 10

    # Verify rule is appended to in-memory store via GET /rules
    rules_resp = client.get("/rules")
    assert rules_resp.status_code == 200
    rules_data = rules_resp.json()
    assert rules_data["total"] == 1
    rule = rules_data["rules"][0]
    assert rule["device_id"] == "warehouse-3"
    assert rule["metric"] == "temperature"
    assert rule["threshold"] == 40.0
    assert rule["duration_minutes"] == 10
