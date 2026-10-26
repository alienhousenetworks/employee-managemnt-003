# Production release gate

This checklist is a hard gate, not a statement that the product has already passed it.

## 1. Configuration and deployment safety

- Copy `.env.example` into the secret manager; never commit live values.
- Set `DJANGO_SECRET_KEY`, exact production `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, CORS origins, TLS and proxy settings.
- Keep `DJANGO_DEBUG=false`; production startup deliberately fails if the secret, host allowlist or production database URL is missing.
- Run the web app and API behind HTTPS. Do not expose the internal AI service directly to browsers.
- Mount a persistent, access-restricted volume for `AI_RUN_STORE_PATH`; SQLite run persistence is a single-instance baseline, not a multi-replica production database.

## 2. Database migration policy

The current CI job uses PostgreSQL 16, generates candidate migrations in its ephemeral workspace, applies them to a clean database, runs `makemigrations --check --dry-run`, and uploads the candidate files as an artifact. It also performs a dump/restore smoke test against a temporary CI database. This does not validate production backup retention, point-in-time recovery, RPO or RTO. Those files are not automatically committed. The latest successful candidate artifact is available from [CI run 40314154429](https://github.com/alienhousenetworks/employee-managemnt-003/actions/runs/40314154429/artifacts/12646650427).

Before deployment:
1. Download the CI artifact named `generated-django-migration-candidates`.
2. Review every migration for data loss, operation order, indexes, constraints and tenant foreign keys.
3. Commit the reviewed files into the corresponding `backend/apps/<app>/migrations/` directories.
4. Update CI to run `python manage.py migrate --noinput` from committed migrations without first generating new migrations.
5. Run `python manage.py makemigrations --check --dry-run` against the committed tree.
6. Test upgrade from the previous release database snapshot and rollback/forward recovery against PostgreSQL.
7. Never use `migrate --run-syncdb` or rely on unmigrated apps for production.

## 3. Backend checks

Run from `backend/` in a configured environment:
```sh
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py migrate --noinput
pytest
```

Verify tenant boundaries with at least two organizations and users who belong to only one organization. Test foreign IDs on every create/update/action endpoint. Expect 403 or a non-disclosing 404 and no database mutation.

## 4. Agency delivery / CRM

- Verify service templates are scoped to the active organization.
- Verify foreign-tenant clients/projects cannot be attached to opportunities, renewals, tasks, deliverables or GitHub links.
- Verify task dependency cycle attempts fail and valid dependencies succeed.
- Verify a deliverable cannot be marked delivered before QA approval.
- Configure GitHub App credentials only in a secret manager; add signature verification, installation permission checks, webhook replay protection and periodic reconciliation before enabling automatic synchronization.

## 5. HR, EOD and approvals

- Verify employee access is limited to their own attendance, leave and EOD records unless an explicit role policy grants more access.
- Test leave date validation, overlapping leave, balance calculations, attendance correction approvals and concurrent check-in requests.
- Verify evidence input is structured and client-supplied data cannot assert `VERIFIED` or `LIVE_VERIFIED`.
- Test every state transition for allowed source status, authorized actor, required note and immutable revision/audit record.
- Payroll remains an approval/export workflow only; do not calculate or pay wages without validated policy, provider integration and finance authorization.

## 6. WhatsApp

- Configure Meta callback verification and signature secrets.
- Confirm invalid signatures fail, webhook retries are idempotent, opt-in is never inferred from inbound messages, and opt-outs immediately block outbound queueing.
- Outbound queueing and approval now fail closed unless `WHATSAPP_APPROVED_TEMPLATES` contains the exact template name; the allowlist must mirror templates approved in Meta WhatsApp Manager. This configuration is not proof of Meta approval by itself.
- Before production sends, add provider-backed sending, retry/dead-letter handling, rate limits and reconciliation of sent/delivered/read/failed statuses. No provider send worker is implemented yet.
- Approval alone must never be reported as delivery.

## 7. AI service

- Keep `AI_PROVIDER=disabled` until a real provider, evidence retrieval, tenant authorization, allowlisted tools, approval checks, cost ceilings and evaluations are enabled.
- Verify the internal service key and organization context on every request.
- Verify run reads require the same organization as the run record.
- Verify an `Idempotency-Key` retry returns the same run only for the same organization and request payload; a changed payload with the same key must return HTTP 409.
- Configure a persistent protected `AI_RUN_STORE_PATH`; back up and restore it. SQLite is still a single-instance persistence baseline, not a durable multi-replica queue.
- Do not send raw HR/private-message data to an AI provider without explicit policy, data minimization, retention and audit controls.

## 8. Web and mobile

- Test login, organization switching, expired token, logout and API-unavailable states.
- Test EOD draft creation/submission, attendance check-in/out and leave request creation against the live API.
- Complete the remaining mobile screens before calling mobile feature parity complete.
- Offline mutations must use an explicit queue, client-generated idempotency key, replay-safe server API and conflict UI. Never silently claim an offline write succeeded remotely.
- Test deep links, push permissions, notification ownership and logout cleanup.

## 9. Operations

- Run a load test using expected concurrent users and peak feed/message traffic.
- Configure structured logs, request IDs, error monitoring, health/readiness probes and alerting.
- Perform a backup and a documented restore into an isolated environment; record measured recovery time.
- Verify secrets rotation, dependency scanning, least-privilege database access, retention/deletion policies and incident response ownership.
- Keep production deployment blocked until all gates have named owners and recorded evidence of passing.
