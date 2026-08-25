def test_get_devices_endpoint(client):
    response = client.get("/devices")
    assert response.status_code == 200
    devices = response.json()
    assert "warehouse-3" in devices
    assert "cold-storage-1" in devices

def test_unsupported_metric_for_existing_device(client):
    """
    Test metric mismatch validation on an existing device.
    front-gate only supports 'camera_status', asking for 'temperature' must fail validation.
    """
    payload = {
        "text": "Alert me if front-gate temperature stays above 40°C for more than 5 minutes"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "validation_error"
    assert data["executed"] is False
    assert any("does not support metric 'temperature'" in err for err in data["errors"])

def test_list_rules_action(client):
    # First create a rule
    client.post("/command", json={"text": "Alert me if warehouse-3 temperature stays above 40°C for 10 minutes"})

    # Execute LIST_RULES action via /command
    response = client.post("/command", json={"text": "show all rules for warehouse-3"})
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["executed"] is True
    assert data["understood_as"]["type"] == "LIST_RULES"
    assert data["data"]["count"] == 1
