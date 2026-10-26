# Phase 3 implementation notes — 2026-10-26

## Added in this phase

- Service-line templates and tenant-scoped CRM opportunity stages.
- Client renewal tracking records.
- Tenant-scoped GitHub repository and work-item link models and API endpoints. Live GitHub App authentication, webhook signatures, event processing and reconciliation are not configured.
- EOD evidence shape validation. Client input cannot mark evidence as VERIFIED or LIVE_VERIFIED.
- Production Django settings fail closed if a production secret, host allowlist or DATABASE_URL is missing.
- FastAPI AI run records are persisted in a SQLite run store and retrieved only when run ID and organization ID match. Provider execution remains BLOCKED; this is not a durable multi-worker workflow engine.
- React EOD draft/submission, attendance check-in/out and leave request forms are connected to backend endpoints.
- CI generates migration candidates, applies them to a clean database, checks model/migration state, and uploads candidates as an artifact.
- Added CRM tenant-isolation and EOD evidence validation tests.
- Added `.env.example` and `docs/PRODUCTION_RELEASE_GATE.md`.

## Still not complete

- CI has to finish for the latest PR commits. Do not claim green until GitHub reports all jobs passed.
- Generated migration files are CI artifacts only and must be reviewed and committed before release.
- Shift schedules and leave balances are models only; policy-driven accrual, APIs, correction approvals and the rest of HR are incomplete.
- Recruitment, onboarding/offboarding, secure documents/signatures, training, expenses and payroll approval/export workflows are incomplete.
- CRM UI, client onboarding journeys, GitHub App auth and event reconciliation are incomplete.
- WhatsApp still lacks provider-backed outbound sending, template validation, dead-letter handling and end-to-end reconciliation.
- AI still lacks tenant-scoped evidence retrieval, allowlisted execution tools, durable queue orchestration, budgets, evaluations and complete approval enforcement.
- Flutter offline sync, push, deep links and complete role-specific screens remain incomplete.
- Load tests, security review, backup restoration and production operational evidence remain release gates.

This note records code added, not a claim of full PRD completion or production readiness.
