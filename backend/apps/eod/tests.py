import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import EODReport

@pytest.mark.django_db
def test_employee_can_create_and_submit_own_eod():
    user = get_user_model().objects.create_user(username="worker", password="strong-password-123")
    org = Organization.objects.create(name="Example Agency", slug="example-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    client = APIClient(); client.force_authenticate(user)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    response = client.post("/api/v1/eod/reports/", {"report_date":"2026-10-26", "completed_work":"Reviewed PR #17", "evidence":[{"type":"github_pr","id":"17"}]}, format="json", **headers)
    assert response.status_code == 201
    report_id = response.data["id"]
    response = client.post(f"/api/v1/eod/reports/{report_id}/submit/", {}, format="json", **headers)
    assert response.status_code == 200
    assert response.data["status"] == EODReport.Status.SUBMITTED
    assert response.data["version"] == 2

@pytest.mark.django_db
def test_eod_requires_active_tenant_membership():
    user = get_user_model().objects.create_user(username="worker2", password="strong-password-123")
    client = APIClient(); client.force_authenticate(user)
    response = client.get("/api/v1/eod/reports/")
    assert response.status_code == 403

@pytest.mark.django_db
def test_eod_review_requires_manager_and_preserves_revision_history():
    User = get_user_model()
    employee = User.objects.create_user(username="eod-employee", password="strong-password-123")
    manager = User.objects.create_user(username="eod-manager", password="strong-password-123")
    org = Organization.objects.create(name="EOD Review Agency", slug="eod-review-agency")
    Membership.objects.create(organization=org, user=employee, role="EMPLOYEE")
    Membership.objects.create(organization=org, user=manager, role="MANAGER")
    report = EODReport.objects.create(organization=org, employee=employee, report_date="2026-10-26", status="SUBMITTED")
    client = APIClient()
    client.force_authenticate(employee)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    denied = client.post(f"/api/v1/eod/reports/{report.id}/review/", {"action": "start_review"}, format="json", **headers)
    assert denied.status_code == 403
    client.force_authenticate(manager)
    started = client.post(f"/api/v1/eod/reports/{report.id}/review/", {"action": "start_review"}, format="json", **headers)
    assert started.status_code == 200
    assert started.data["status"] == "IN_REVIEW"
    missing_note = client.post(f"/api/v1/eod/reports/{report.id}/review/", {"action": "needs_changes"}, format="json", **headers)
    assert missing_note.status_code == 400
    returned = client.post(f"/api/v1/eod/reports/{report.id}/review/", {"action": "needs_changes", "note": "Please add evidence"}, format="json", **headers)
    assert returned.status_code == 200
    report.refresh_from_db()
    assert report.status == "NEEDS_CHANGES"
    assert report.version == 3
    assert report.revisions.count() == 2

@pytest.mark.django_db
def test_eod_evidence_requires_structured_reference_and_rejects_client_verification():
    User = get_user_model()
    employee = User.objects.create_user(username="eod-evidence", password="strong-password-123")
    org = Organization.objects.create(name="Evidence Agency", slug="evidence-agency")
    Membership.objects.create(organization=org, user=employee, role="EMPLOYEE")
    client = APIClient()
    client.force_authenticate(employee)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    invalid = client.post("/api/v1/eod/reports/", {"report_date": "2026-10-26", "evidence": [{"title": "Commit"}]}, format="json", **headers)
    assert invalid.status_code == 400
    forged = client.post("/api/v1/eod/reports/", {"report_date": "2026-10-26", "evidence": [{"title": "Commit", "type": "github", "reference": "https://github.com/example/repo/commit/abc", "verification_status": "LIVE_VERIFIED"}]}, format="json", **headers)
    assert forged.status_code == 400
    valid = client.post("/api/v1/eod/reports/", {"report_date": "2026-10-26", "evidence": [{"title": "Commit", "type": "github", "reference": "https://github.com/example/repo/commit/abc"}]}, format="json", **headers)
    assert valid.status_code == 201
