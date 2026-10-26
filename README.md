# Agency Workforce OS

A custom-built, multi-service agency operating system for software development, AI/automation, digital marketing, creative, sales, delivery and workforce operations.

## Architecture

- `backend/`: Django + Django REST Framework, PostgreSQL-owned core business domains.
- `ai_services/`: FastAPI AI and integration boundary; no unrestricted database access.
- `web/`: React + TypeScript + Vite employee and management workspace.
- `mobile/`: Flutter Android/iOS client.
- `infra/`: local development, CI and deployment configuration.
- `docs/`: architecture decisions, API contracts, security and runbooks.

## Important product constraints

- This is custom software built from zero. ERPNext/Frappe is not a runtime dependency or application foundation.
- Each record type has one authoritative owner. Mobile and web clients use authenticated APIs only.
- Tenant and object-level authorization is enforced server-side.
- AI actions are typed, permission-checked, auditable and approval-gated. AI must not invent records or claim unverified success.
- Integrations explicitly report `NOT_CONFIGURED`, `UNAVAILABLE`, or verified states.
- HR data, private messages, client records and financial fields have separate access policies.

## Initial development workflow

1. Build and test the Django foundation and API contract.
2. Add FastAPI service authentication, AI run records and safe tool execution.
3. Build React workflows against the versioned API.
4. Build Flutter workflows against the same API.
5. Add integrations, end-to-end tests, security hardening and deployment automation.

## Local development

See `docs/DEVELOPMENT.md` for the planned local environment. Secrets must be supplied through environment variables and must never be committed.

## Status

The repository was initialized for a clean custom implementation. Features are considered complete only after implementation, automated tests and relevant integration verification; this README is not a claim that the product is production-ready.