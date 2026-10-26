import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Organization, Membership

@pytest.mark.django_db
def test_employee_directory_requires_membership():
    user = get_user_model().objects.create_user(username="outsider", password="strong-password-123")
    org = Organization.objects.create(name="Private Agency", slug="private-agency")
    client = APIClient(); client.force_authenticate(user)
    response = client.get("/api/v1/employees/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 403
