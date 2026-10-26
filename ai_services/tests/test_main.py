from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_run_requires_service_auth():
    response = client.post("/api/v1/runs", json={"workflow":"draft_eod","organization_id":"org","instruction":"Draft my EOD"})
    assert response.status_code == 401

def test_disabled_provider_does_not_fabricate_result(monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "test-secret")
    monkeypatch.setenv("AI_PROVIDER", "disabled")
    response = client.post("/api/v1/runs", headers={"X-Service-Key":"test-secret"}, json={"workflow":"draft_eod","organization_id":"org","instruction":"Draft my EOD","source_record_ids":[]})
    assert response.status_code == 200
    assert response.json()["status"] == "BLOCKED"
    assert response.json()["evidence_record_ids"] == []
