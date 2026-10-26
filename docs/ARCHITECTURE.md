# Architecture and ownership

## Decision
Build a custom application. ERPNext/Frappe is not a dependency and is not used as the foundation.

## Domain ownership
- Django/PostgreSQL: organizations, memberships, employee-facing profiles, feed, projects, tasks, EOD reports, approvals, audit events, integration metadata and internal messaging.
- FastAPI: AI execution runtime, provider adapters, tool invocations and evaluation artifacts. AI service calls Django through authenticated APIs for business records.
- WhatsApp, GitHub, Figma and calendar providers remain authoritative for provider-owned delivery/event status. Store references and reconciled projections only.
- Flutter and React are clients and never connect directly to databases or Redis.

## Security boundaries
Tenant membership and object permissions are checked on every request. Never trust organization/user IDs from client payloads without checking membership. AI tool permissions are rechecked immediately before execution. External content is untrusted input. Sensitive actions use explicit approval state transitions and audit records.

## Reliability
State changes that emit events should use a transactional outbox. Consumers are idempotent. Provider webhook IDs are deduplicated. Integration states distinguish NOT_CONFIGURED, UNAVAILABLE, HEALTHY and DEGRADED. Never substitute fabricated zeroes for unavailable data.

## Deployment shape
Begin as a modular Django application and a separately deployable FastAPI service. Use PostgreSQL, Redis and a worker process. Add a durable workflow engine only when long-running approval/recovery requirements justify it.
