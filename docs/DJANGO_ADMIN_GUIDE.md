# Built-in Django administration

The Administration item in the web workspace opens Django's built-in admin at `/admin/`. We use Django admin rather than building a second custom CRUD console for system-level records.

## Local setup

From the repository's backend directory, with the project's virtual environment and dependencies active:

```sh
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://localhost:8000/admin/` and sign in using the superuser credentials created above. In a deployed environment, use the HTTPS backend hostname and create the initial administrator through the approved deployment procedure. Do not commit credentials or use a shared administrator account.

## Registered control areas

- Organizations and memberships
- Employee profiles, notifications and direct-message records
- Company feed posts, comments and reactions
- Clients, projects, tasks, dependencies, deliverables, service templates, opportunities and renewals
- GitHub repository links, linked work items and webhook delivery ledger
- Attendance, leave, correction requests, shifts, leave balances and recruitment candidates
- Approval requests
- EOD reports and immutable revision history
- Audit events
- WhatsApp integration settings, contacts and message history

## Important safety behavior

- Django admin authentication is separate from the JWT login used by the React workspace. A normal API account does not automatically have Django admin access.
- Django admin requires a Django staff account and the relevant model permissions. Grant staff status and model permissions only to trusted administrators.
- This admin is a system-level control surface, not a tenant-scoped replacement for the employee application. Do not grant staff access to users who should only see one agency unless organization-level admin queryset and object-permission enforcement has been implemented and reviewed.
- EOD reports/revisions, audit events, approval decisions, attendance state, leave decisions and WhatsApp message history are protected against routine editing in the admin. Use the application's authorized workflow endpoints to make business decisions.
- A Django superuser can bypass normal application workflows. Keep superuser accounts limited, use MFA at the identity/proxy layer where available, protect sessions, log admin activity and review access regularly.
- Do not store provider secrets in model text fields. Keep secrets in the deployment secret manager.
- Before production, test model permissions with a non-superuser staff account, check the admin audit trail, enable HTTPS and validate CSRF/session-cookie settings.

## Known limitation

Django's default admin permissions are model-level, not agency-tenant-level. The current admin registrations are intended for trusted system administrators. Organization-specific administrator access needs additional tenant-scoped querysets, related-object form filtering and object-level permission tests before it is safe to delegate to individual agency admins.
