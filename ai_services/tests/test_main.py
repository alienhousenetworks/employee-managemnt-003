import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolated_run_store(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_RUN_STORE_PATH", str(tmp_path / "runs.sqlite3"))

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_run_requires_service_auth():
    response = client.post("/api/v1/runs", json={"workflow":"draft_eod","organization_id":"org","instruction":"Draft my EOD"}, headers={"X-Organization-ID":"org"})
    assert response.status_code == 401

def test_run_requires_matching_organization_context(monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "test-secret")
    response = client.post("/api/v1/runs", headers={"X-Service-Key":"test-secret","X-Organization-ID":"org-b"}, json={"workflow":"draft_eod","organization_id":"org-a","instruction":"Draft my EOD"})
    assert response.status_code == 403

def test_disabled_provider_persists_blocked_run_without_fabricating_result(monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "test-secret")
    monkeypatch.setenv("AI_PROVIDER", "disabled")
    headers = {"X-Service-Key":"test-secret","X-Organization-ID":"org"}
    response = client.post("/api/v1/runs", headers=headers, json={"workflow":"draft_eod","organization_id":"org","instruction":"Draft my EOD","source_record_ids":[]})
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "BLOCKED"
    assert result["evidence_record_ids"] == []
    read = client.get(f"/api/v1/runs/{result['run_id']}?organization_id=org", headers=headers)
    assert read.status_code == 200
    assert read.json()["status"] == "BLOCKED"
    foreign = client.get(f"/api/v1/runs/{result['run_id']}?organization_id=another-org", headers={"X-Service-Key":"test-secret","X-Organization-ID":"another-org"})
    assert foreign.status_code == 404


def test_run_idempotency_returns_same_run_and_rejects_changed_payload(monkeypatch):
    monkeypatch.setenv("SERVICE_API_KEY", "test-secret")
    monkeypatch.setenv("AI_PROVIDER", "disabled")
    headers = {
        "X-Service-Key": "test-secret",
        "X-Organization-ID": "org-idempotent",
        "Idempotency-Key": "daily-eod-2026-10-26-user-42",
    }
    payload = {
        "workflow": "draft_eod",
        "organization_id": "org-idempotent",
        "instruction": "Draft today's EOD from verified records",
        "source_record_ids": ["eod-42"],
    }
    first = client.post("/api/v1/runs", headers=headers, json=payload)
    second = client.post("/api/v1/runs", headers=headers, json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["run_id"] == second.json()["run_id"]

    changed = {**payload, "instruction": "Draft a different report"}
    conflict = client.post("/api/v1/runs", headers=headers, json=changed)
    assert conflict.status_code == 409

    other_org = client.post(
        "/api/v1/runs",
        headers={**headers, "X-Organization-ID": "other-org", "Idempotency-Key": headers["Idempotency-Key"]},
        json={**payload, "organization_id": "other-org"},
    )
    assert other_org.status_code == 200
    assert other_org.json()["run_id"] != first.json()["run_id"]
