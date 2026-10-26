import os
import sqlite3
from pathlib import Path

def connect():
    path = Path(os.getenv("AI_RUN_STORE_PATH", "./var/ai-runs.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS workflow_runs (run_id TEXT PRIMARY KEY, organization_id TEXT NOT NULL, workflow TEXT NOT NULL, status TEXT NOT NULL, mode TEXT NOT NULL, message TEXT NOT NULL, evidence_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_runs_org ON workflow_runs(organization_id, created_at)")
    return db

def save_run(run):
    with connect() as db:
        db.execute("INSERT INTO workflow_runs(run_id, organization_id, workflow, status, mode, message, evidence_json) VALUES(?,?,?,?,?,?,?)", (run["run_id"], run["organization_id"], run["workflow"], run["status"], run["mode"], run["message"], "[]"))
        row = db.execute("SELECT * FROM workflow_runs WHERE run_id=? AND organization_id=?", (run["run_id"], run["organization_id"])).fetchone()
        return dict(row)

def find_run(run_id, organization_id):
    with connect() as db:
        row = db.execute("SELECT * FROM workflow_runs WHERE run_id=? AND organization_id=?", (run_id, organization_id)).fetchone()
        return dict(row) if row else None
