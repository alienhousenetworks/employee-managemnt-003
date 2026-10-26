import os
import sqlite3
from contextlib import closing
from pathlib import Path


def connect():
    path = Path(os.getenv("AI_RUN_STORE_PATH", "./var/ai-runs.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute(
        "CREATE TABLE IF NOT EXISTS workflow_runs ("
        "run_id TEXT PRIMARY KEY, organization_id TEXT NOT NULL, workflow TEXT NOT NULL, "
        "status TEXT NOT NULL, mode TEXT NOT NULL, message TEXT NOT NULL, "
        "evidence_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    columns = {row["name"] for row in db.execute("PRAGMA table_info(workflow_runs)")}
    if "idempotency_key" not in columns:
        db.execute("ALTER TABLE workflow_runs ADD COLUMN idempotency_key TEXT")
    if "request_hash" not in columns:
        db.execute("ALTER TABLE workflow_runs ADD COLUMN request_hash TEXT")
    db.execute("CREATE INDEX IF NOT EXISTS idx_runs_org ON workflow_runs(organization_id, created_at)")
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_runs_org_idempotency "
        "ON workflow_runs(organization_id, idempotency_key) WHERE idempotency_key IS NOT NULL"
    )
    return db


def save_run(run):
    with closing(connect()) as db, db:
        db.execute(
            "INSERT OR IGNORE INTO workflow_runs"
            "(run_id, organization_id, workflow, status, mode, message, evidence_json, idempotency_key, request_hash) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                run["run_id"], run["organization_id"], run["workflow"], run["status"],
                run["mode"], run["message"], "[]", run.get("idempotency_key"), run.get("request_hash"),
            ),
        )
        if run.get("idempotency_key"):
            row = db.execute(
                "SELECT * FROM workflow_runs WHERE organization_id=? AND idempotency_key=?",
                (run["organization_id"], run["idempotency_key"]),
            ).fetchone()
            if row and run.get("request_hash") and row["request_hash"] and row["request_hash"] != run["request_hash"]:
                raise ValueError("Idempotency-Key was already used with a different request.")
        else:
            row = db.execute(
                "SELECT * FROM workflow_runs WHERE run_id=? AND organization_id=?",
                (run["run_id"], run["organization_id"]),
            ).fetchone()
        return dict(row) if row else None


def find_run(run_id, organization_id):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM workflow_runs WHERE run_id=? AND organization_id=?",
            (run_id, organization_id),
        ).fetchone()
        return dict(row) if row else None
