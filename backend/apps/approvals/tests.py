import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import ApprovalRequest

@pytest.mark.django_db
def test_employee_can_request_approval_but_cannot_decide_it():
    user = get_user_model().objects.create_user(username="requester", password="strong-password-123")
    org = Organization.objects.create(name="Approval Agency", slug="approval-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    client = APIClient(); client.force_authenticate(user)
    headers = {"HTTP_X_ORGANIZATION_ID": str(org.id)}
    created = client.post("/api/v1/approvals/", {"action_type":"publish_campaign", "target_type":"campaign", "target_id":"camp-1", "reason":"Requesting approval", "payload":{"campaign":"camp-1"}}, format="json", **headers)
    assert created.status_code == 201
    decision = client.post(f"/api/v1/approvals/{created.data['id']}/decision/", {"decision":"approve"}, format="json", **headers)
    assert decision.status_code == 403
    assert ApprovalRequest.objects.get(id=created.data["id"]).status == ApprovalRequest.Status.PENDING
