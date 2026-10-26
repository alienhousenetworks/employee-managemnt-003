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
