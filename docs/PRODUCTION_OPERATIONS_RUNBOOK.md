# Production Operations and Recovery Runbook

This runbook is a template for operators of Agency Workforce OS. It does not replace a tested environment-specific disaster-recovery plan. Do not run destructive commands against production until the database, backup location, maintenance window and rollback owner are confirmed.

## Release prerequisites

- Use PostgreSQL, not SQLite, for production.
- Configure `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, HTTPS/proxy settings, CORS origins, JWT lifetimes and secret storage through the deployment secret manager.
- Pin application/container versions and record the deployed Git SHA.
- Review and commit Django migrations before deployment. A CI-generated migration artifact is only a candidate; it is not a substitute for committed migrations.
- Confirm outbound providers are configured explicitly. Missing credentials must leave a feature unavailable, not simulate success.
- Confirm on-call owner, maintenance window, backup destination and recovery point objective (RPO) / recovery time objective (RTO).

## Pre-deployment database procedure

1. Confirm the deployment is targeting the intended database and tenant environment.
2. Verify the database backup completed and is readable. Record timestamp, object location, size and checksum.
3. In staging, restore the latest backup into a separate database and run smoke tests against the restored copy.
4. Run `python manage.py showmigrations` and inspect the planned migration set.
5. Apply migrations to staging using `python manage.py migrate --plan` followed by `python manage.py migrate --noinput`.
6. Run the backend test suite, tenant-isolation tests and key workflow smoke tests against PostgreSQL.
7. Deploy the exact tested commit. Apply migrations once through the designated release job, not concurrently from every web replica.
8. Run post-deployment checks: authentication, organization boundary checks, attendance/leave, client/project creation, feed, EOD, provider health and error rates.

## Rollback and recovery

- Application rollback: revert to the last known-good immutable application image/commit only after checking backward compatibility with the already-applied schema.
- Schema rollback: do not assume every migration is safely reversible. Review each migration's reverse operations and data-loss implications. Prefer a forward corrective migration for destructive or data-transforming changes.
- Database recovery: restore the most recent verified backup to a *new* database/instance, validate migration history and key row counts, run smoke tests, then switch traffic only with the incident commander’s approval.
- Do not overwrite the failed production database during recovery. Preserve it for investigation until recovery is confirmed.
- Capture the incident timeline, deployed SHA, migration list, backup timestamp, restore duration, data-loss estimate and approval decision.

## Backup restoration acceptance criteria

- Restore command exits successfully and schema objects exist.
- Django migration history is present and consistent with the tested release.
- Authentication and tenant-scoped read/write smoke tests pass.
- A representative set of records can be read and relational constraints remain valid.
- The measured restore duration meets the documented RTO and the restored data point meets the RPO.
- The incident/recovery owner signs off before traffic is switched.

## Security and tenant-isolation checks

- Test cross-organization reads and writes for every list/detail/action endpoint, including guessed UUIDs.
- Confirm user assignment fields only accept active members of the active organization.
- Check manager-only actions, object-level permissions, audit events and denied actions.
- Verify webhook signatures, replay/idempotency handling, secret rotation and redaction of credentials/PII from logs.
- Test rate limits, upload size/type restrictions, CORS/CSRF policy, secure cookies, HTTPS redirects and JWT expiry/rotation.
- Run dependency, static-analysis and vulnerability scans; track findings with severity and owner.

## Operational signals and incident response

Alert on elevated 5xx/latency, failed jobs, queue age, provider failures, repeated webhook signature errors, authentication failures, database saturation and backup age/failure.

For an incident:
1. Record incident start and affected tenants/features.
2. Disable the affected integration or outbound worker if continued execution could duplicate or leak data.
3. Preserve logs and job/provider IDs with secrets and personal data redacted.
4. Identify the last known-good deployment and data checkpoint.
5. Apply rollback/recovery only after impact and data-loss risks are reviewed.
6. Verify recovery with tenant-scoped smoke tests and notify affected stakeholders.
7. Document root cause, corrective actions, owner and due date.

## CI evidence and limitations

CI's PostgreSQL service and backup-restore smoke test validate the test schema generated during the workflow. They do **not** prove that production backups, retention policies, point-in-time recovery, replicas, monitoring or RTO/RPO are configured. Committed migration files and a staging rehearsal remain required release gates.
