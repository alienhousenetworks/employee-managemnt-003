import hmac
import os
import uuid
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from .schemas import RunRequest, RunResponse
from .run_store import save_run, find_run

app = FastAPI(title="Agency Workforce AI Service", version="0.2.0")

def verify_service_key(x_service_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("SERVICE_API_KEY", "")
    if not expected or not x_service_key or not hmac.compare_digest(expected, x_service_key):
        raise HTTPException(status_code=401, detail="Valid service credentials are required.")

@app.get("/health/live")
def liveness():
    return {"status": "ok", "service": "agency-workforce-ai"}

@app.get("/health/ready")
def readiness():
    configured = bool(os.getenv("SERVICE_API_KEY"))
    return {"status": "ready" if configured else "not_configured", "authentication_configured": configured, "provider_mode": os.getenv("AI_PROVIDER", "disabled")}

@app.post("/api/v1/runs", response_model=RunResponse, dependencies=[Depends(verify_service_key)])
def create_run(request: RunRequest, x_organization_id: str | None = Header(default=None)):
    if not x_organization_id or not hmac.compare_digest(x_organization_id, request.organization_id):
        raise HTTPException(status_code=403, detail="The organization header must match the authenticated request context.")
    run_id = str(uuid.uuid4())
    if os.getenv("AI_PROVIDER", "disabled").lower() == "disabled":
        result = RunResponse(run_id=run_id, status="BLOCKED", mode="PROVIDER_DISABLED", message="AI provider is not configured. No work was executed and no result was fabricated.", evidence_record_ids=[])
    else:
        result = RunResponse(run_id=run_id, status="BLOCKED", mode="RULE_BASED", message="Execution is blocked until tenant-scoped evidence retrieval, authorized tools, approval policy and provider verification are configured.", evidence_record_ids=[])
    save_run({"run_id": result.run_id, "organization_id": request.organization_id, "workflow": request.workflow, "status": result.status, "mode": result.mode, "message": result.message})
    return result

@app.get("/api/v1/runs/{run_id}", dependencies=[Depends(verify_service_key)])
def read_run(run_id: str, organization_id: str = Query(...), x_organization_id: str | None = Header(default=None)):
    if not x_organization_id or not hmac.compare_digest(x_organization_id, organization_id):
        raise HTTPException(status_code=403, detail="The organization header must match the request context.")
    record = find_run(run_id, organization_id)
    if not record:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {"run_id": record["run_id"], "organization_id": record["organization_id"], "workflow": record["workflow"], "status": record["status"], "mode": record["mode"], "message": record["message"], "evidence_record_ids": []}
