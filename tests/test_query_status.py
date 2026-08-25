def test_status_query(client):
    """
    Mandatory Test 2: Status Query
    Prompt: 'what's the humidity in cold-storage-1 right now'
    Expected: QUERY_STATUS parsed, executed successfully, returns telemetry data.
    """
    payload = {
        "text": "what's the humidity in cold-storage-1 right now"
    }
    response = client.post("/command", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "success"
    assert data["executed"] is True
    assert data["understood_as"]["type"] == "QUERY_STATUS"
    assert data["understood_as"]["device_id"] == "cold-storage-1"
    assert data["understood_as"]["metric"] == "humidity"
    assert data["data"]["value"] == 82.0
