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
