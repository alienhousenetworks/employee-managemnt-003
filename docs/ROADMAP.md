# Delivery roadmap and completion gates

## Foundation (current branch)
- [x] Initialize repository and architecture ownership rules.
- [x] Add initial Django domains for organizations, memberships, employee directory, feed and delivery records.
- [x] Add FastAPI service boundary that fails closed without configured execution.
- [x] Add React/Vite shell and Flutter app shell.
- [ ] Generate and review Django migrations; run backend tests in a real environment.
- [ ] Add complete authorization tests and resolve all findings before merging.

## Next implementation slices
1. Authentication/session lifecycle, tenant-scoped object permissions, invitation/onboarding and audit instrumentation.
2. Feed visibility, comments/reactions, attachments, notifications, internal messaging and search.
3. Projects/tasks, service-line templates, client handover, EOD workflow and approvals.
4. Custom HR workflows (employee lifecycle, shifts, leave, attendance, documents, training, expenses) with policy and audit requirements.
5. CRM pipeline, proposal approvals, renewals and sales-to-delivery handover.
6. WhatsApp Business webhook verification, consent/templates, outbound queue and delivery reconciliation.
7. FastAPI AI run persistence, source-bound retrieval, scoped tools, approvals, evaluation and cost controls.
8. Flutter auth, secure token storage, offline queue/idempotency, push and deep links.
9. Role-specific analytics with metric definitions, data freshness and authoritative sources.
10. Security, accessibility, load, backup/restore, operational runbooks and staged rollout.

## Release rule
A navigation screen or model is not an end-to-end feature. Each slice requires migrations, API tests, authorization tests, frontend/mobile journeys, failure recovery and acceptance evidence. Do not claim production readiness until the complete release scope passes.
