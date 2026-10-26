# Implementation status — Agency Workforce OS

Last updated: 2026-10-26

## Implemented in the current development branch

- Custom Django/DRF API foundation, JWT authentication, organization membership checks and organization-scoped core records.
- Employee directory API with search and department filtering.
- Team feed posts, comments, reactions and visibility rules for organization, department and author-private posts.
- HR foundation: attendance check-in/check-out, leave requests and manager decisions, employee requests.
- Approval requests with role-gated human decisions. Approval records a decision; it does not execute arbitrary actions.
- EOD report submission and manager review transitions with revision records and version increments.
- Agency delivery records for clients, projects and tasks.
- Task dependencies with same-project/tenant validation and cycle prevention.
- Project deliverables with explicit QA/delivery state transitions and manager-gated QA decisions.
- Direct messages restricted to sender/recipient and active organization; notification listing and recipient-only read acknowledgement.
- WhatsApp foundation: signed webhook validation, idempotent inbound message ingestion, opt-in/opt-out records, opt-in-required outbound queueing and manager approval. Approval is not provider delivery.
- React sign-in, organization selection, feed, employee directory, direct messaging and notification views.
- Flutter sign-in and feed-connected workspace shell.
- GitHub Actions CI workflow for backend, AI service, web and Flutter.

## Known gaps — do not treat these as production-ready

- The latest CI run observed before the most recent commits had backend/web/AI-service passing but Flutter analysis failing on syntax errors. Those Flutter files were corrected afterward; a fresh CI result still needs to be confirmed.
- Database migrations are not yet generated/reviewed for the expanded domain models. The current test bootstrap relies on unmigrated-app table creation; production deployment must not rely on that.
- WhatsApp provider credentials, webhook configuration, provider-backed outbound worker, delivery retries/reconciliation and production consent evidence capture remain to be configured/implemented.
- Direct messages are a basic message stream, not yet full conversations with attachments, delivery/read receipts, retention policy or push delivery.
- Notifications have read-state APIs but event producers, preferences, push delivery and deep links are incomplete.
- Client onboarding journeys, service-line templates, CRM pipeline stages, renewals, GitHub issue/PR linking, file storage and richer QA evidence are incomplete.
- HR shift calendars, leave accrual/balances, attendance corrections, recruitment, onboarding/offboarding, document workflows, training, expenses and payroll approvals remain incomplete.
- AI workflow persistence, durable orchestration, tenant-scoped retrieval, tool allowlists, budget enforcement, evaluations and end-to-end approval enforcement need more work.
- Flutter is not yet a complete mobile app: offline synchronization, push notifications, deep links, role-specific screens and end-to-end journeys remain outstanding.
- Security review, tenant-isolation matrix, load testing, backup/restore drill, migration rollback test and operational runbooks remain release gates.

## Current API routes added or expanded

- `GET /api/v1/employees/`
- `GET|POST /api/v1/employees/messages/`
- `GET /api/v1/employees/notifications/`
- `POST /api/v1/employees/notifications/<id>/read/`
- `POST /api/v1/eod/reports/<id>/review/`
- `GET|POST /api/v1/delivery/task-dependencies/`
- `GET|POST /api/v1/delivery/deliverables/`
- `POST /api/v1/delivery/deliverables/<id>/transition/`
- `GET|POST /api/v1/whatsapp/contacts/`
- `POST /api/v1/whatsapp/contacts/<id>/consent/`
- `GET|POST /api/v1/whatsapp/messages/`
- `POST /api/v1/whatsapp/messages/<id>/approve/`
- `GET|POST /api/v1/whatsapp/webhook/` (provider verification and signed webhook)

## Release gate

Do not deploy this branch to production until the latest CI passes, database migrations are generated and reviewed, secrets are configured, tenant and role isolation tests pass, WhatsApp provider setup is verified, and backup/restore plus operational checks are completed.
