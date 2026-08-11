import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_models_endpoint():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    models = data["data"]
    ids = [m["id"] for m in models]
    assert "neurix" in ids
    assert "logix" in ids
    assert "optix" in ids

def test_chat_completions_streaming_endpoint():
    payload = {
        "model": "neurix",
        "messages": [
            {"role": "user", "content": "Explain ProX AI model platform"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    lines = [line.strip() for line in response.text.split("\n") if line.strip()]
    assert len(lines) > 0
    assert lines[-1] == "data: [DONE]"
