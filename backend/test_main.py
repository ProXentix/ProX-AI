import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    model_ids = [m["id"] for m in data["data"]]
    assert "neurix" in model_ids
    assert "logix" in model_ids
    assert "optix" in model_ids

def test_chat_completions_stream():
    payload = {
        "model": "logix",
        "messages": [
            {"role": "user", "content": "Write a React component code"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    lines = [line.strip() for line in response.text.split("\n") if line.strip()]
    assert len(lines) > 0
    assert lines[-1] == "data: [DONE]"
