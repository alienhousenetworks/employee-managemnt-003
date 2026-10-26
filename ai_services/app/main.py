import hmac
import os
import uuid
from fastapi import Depends, FastAPI, Header, HTTPException
from .schemas import RunRequest, RunResponse

app = FastAPI(title="Agency Workforce AI Service", version="0.1.0")

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
def create_run(request: RunRequest):
    # This foundation intentionally refuses to invent results. Provider execution is not
    # enabled until a tenant-scoped evidence adapter, policy checks and durable run store exist.
    run_id = str(uuid.uuid4())
    if os.getenv("AI_PROVIDER", "disabled").lower() == "disabled":
        return RunResponse(run_id=run_id, status="BLOCKED", mode="PROVIDER_DISABLED", message="AI provider is not configured. No work was executed and no result was fabricated.", evidence_record_ids=[])
    return RunResponse(run_id=run_id, status="BLOCKED", mode="RULE_BASED", message="Execution is blocked until evidence retrieval, durable run persistence, tenant authorization and approval policy are configured.", evidence_record_ids=[])
