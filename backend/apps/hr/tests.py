import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import LeaveRequest

@pytest.mark.django_db
def test_leave_request_validation_and_employee_scope():
    user = get_user_model().objects.create_user(username="hr-worker", password="strong-password-123")
    org = Organization.objects.create(name="HR Test Agency", slug="hr-test-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    client = APIClient(); client.force_authenticate(user)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    invalid = client.post("/api/v1/hr/leave/", {"leave_type":"ANNUAL", "start_date":"2026-11-10", "end_date":"2026-11-09"}, format="json", **headers)
    assert invalid.status_code == 400
    valid = client.post("/api/v1/hr/leave/", {"leave_type":"ANNUAL", "start_date":"2026-11-10", "end_date":"2026-11-11", "reason":"Personal leave"}, format="json", **headers)
    assert valid.status_code == 201
    assert valid.data["status"] == LeaveRequest.Status.SUBMITTED

@pytest.mark.django_db
def test_overlapping_submitted_leave_is_rejected_but_non_overlapping_leave_is_allowed():
    user = get_user_model().objects.create_user(username="hr-overlap-worker", password="strong-password-123")
    org = Organization.objects.create(name="Leave Overlap Agency", slug="leave-overlap-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    client = APIClient()
    client.force_authenticate(user)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    first = client.post(
        "/api/v1/hr/leave/",
        {"leave_type": "ANNUAL", "start_date": "2026-11-10", "end_date": "2026-11-12"},
        format="json", **headers,
    )
    assert first.status_code == 201
    overlap = client.post(
        "/api/v1/hr/leave/",
        {"leave_type": "SICK", "start_date": "2026-11-12", "end_date": "2026-11-13"},
        format="json", **headers,
    )
    assert overlap.status_code == 400
    assert "overlaps" in str(overlap.data).lower()
    separate = client.post(
        "/api/v1/hr/leave/",
        {"leave_type": "SICK", "start_date": "2026-11-13", "end_date": "2026-11-14"},
        format="json", **headers,
    )
    assert separate.status_code == 201


@pytest.mark.django_db
def test_employee_cannot_read_another_organizations_leave_requests():
    User = get_user_model()
    employee_a = User.objects.create_user(username="hr-tenant-a", password="strong-password-123")
    employee_b = User.objects.create_user(username="hr-tenant-b", password="strong-password-123")
    org_a = Organization.objects.create(name="HR Tenant A", slug="hr-tenant-a")
    org_b = Organization.objects.create(name="HR Tenant B", slug="hr-tenant-b")
    Membership.objects.create(organization=org_a, user=employee_a, role="EMPLOYEE")
    Membership.objects.create(organization=org_b, user=employee_b, role="EMPLOYEE")
    LeaveRequest.objects.create(
        organization=org_b, employee=employee_b, leave_type="ANNUAL",
        start_date="2026-12-01", end_date="2026-12-02",
    )
    client = APIClient()
    client.force_authenticate(employee_a)
    response = client.get("/api/v1/hr/leave/", HTTP_X_ORGANIZATION_ID=str(org_a.id))
    assert response.status_code == 200
    rows = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
    assert len(rows) == 0
