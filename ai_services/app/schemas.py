from typing import Literal
from pydantic import BaseModel, Field

class RunRequest(BaseModel):
    workflow: Literal["summarize_project", "draft_eod", "classify_blocker"]
    organization_id: str
    source_record_ids: list[str] = Field(default_factory=list, max_length=50)
    instruction: str = Field(min_length=1, max_length=4000)

class RunResponse(BaseModel):
    run_id: str
    status: Literal["RECEIVED", "BLOCKED", "COMPLETED"]
    mode: Literal["RULE_BASED", "PROVIDER_DISABLED"]
    message: str
    evidence_record_ids: list[str] = Field(default_factory=list)
