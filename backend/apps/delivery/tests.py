import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import Project, Task, TaskDependency, ProjectDeliverable

@pytest.mark.django_db
def test_task_dependency_rejects_cycles():
    user = get_user_model().objects.create_user(username="delivery-owner", password="strong-password-123")
    org = Organization.objects.create(name="Delivery Agency", slug="delivery-agency")
    Membership.objects.create(organization=org, user=user, role="MANAGER", department="Delivery")
    project = Project.objects.create(organization=org, name="Website", service_line="DEVELOPMENT")
    first = Task.objects.create(organization=org, project=project, title="Design", created_by=user)
    second = Task.objects.create(organization=org, project=project, title="Build", created_by=user)
    TaskDependency.objects.create(organization=org, predecessor=first, successor=second, created_by=user)
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/task-dependencies/", {"predecessor": str(second.id), "successor": str(first.id)}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400
    assert TaskDependency.objects.count() == 1

@pytest.mark.django_db
def test_deliverable_requires_qa_approval_before_delivery():
    user = get_user_model().objects.create_user(username="delivery-manager", password="strong-password-123")
    org = Organization.objects.create(name="QA Agency", slug="qa-agency")
    Membership.objects.create(organization=org, user=user, role="MANAGER", department="Engineering")
    project = Project.objects.create(organization=org, name="Release", service_line="DEVELOPMENT")
    item = ProjectDeliverable.objects.create(organization=org, project=project, title="Release candidate", created_by=user, status="IN_PROGRESS")
    client = APIClient()
    client.force_authenticate(user)
    early = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "deliver"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert early.status_code == 400
    submitted = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "submit_qa"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert submitted.status_code == 200
    approved = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "qa_pass", "note": "Acceptance criteria verified"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert approved.status_code == 200
    delivered = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "deliver"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert delivered.status_code == 200
    item.refresh_from_db()
    assert item.status == "DELIVERED"
    assert item.version == 4

@pytest.mark.django_db
def test_deliverable_cannot_reference_another_tenant_project():
    user = get_user_model().objects.create_user(username="delivery-member", password="strong-password-123")
    org = Organization.objects.create(name="Own Agency", slug="own-agency")
    other = Organization.objects.create(name="Other Agency", slug="other-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    project = Project.objects.create(organization=other, name="Foreign", service_line="AI")
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/deliverables/", {"project": str(project.id), "title": "Should be blocked"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400
    assert not ProjectDeliverable.objects.filter(organization=org).exists()

@pytest.mark.django_db
def test_opportunity_rejects_foreign_tenant_client():
    user = get_user_model().objects.create_user(username="crm-manager", password="strong-password-123")
    org = Organization.objects.create(name="CRM Agency", slug="crm-agency")
    other = Organization.objects.create(name="Foreign CRM", slug="foreign-crm")
    Membership.objects.create(organization=org, user=user, role="SALES")
    foreign_client = __import__("apps.delivery.models", fromlist=["ClientAccount"]).ClientAccount.objects.create(organization=other, name="Foreign Client")
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/opportunities/", {"client": str(foreign_client.id), "name": "Test opportunity", "service_line": "AI", "probability_percent": 25}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400

@pytest.mark.django_db
def test_service_template_is_organization_scoped():
    from .models import ServiceTemplate
    user = get_user_model().objects.create_user(username="template-manager", password="strong-password-123")
    org = Organization.objects.create(name="Template Agency", slug="template-agency")
    other = Organization.objects.create(name="Other Templates", slug="other-templates")
    Membership.objects.create(organization=org, user=user, role="MANAGER")
    ServiceTemplate.objects.create(organization=other, service_line="AI", name="Foreign template")
    client = APIClient()
    client.force_authenticate(user)
    response = client.get("/api/v1/delivery/service-templates/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_project_rejects_foreign_tenant_manager_and_task_assignee():
    User = get_user_model()
    member = User.objects.create_user(username="delivery-local-member", password="strong-password-123")
    foreign = User.objects.create_user(username="delivery-foreign-member", password="strong-password-123")
    org = Organization.objects.create(name="Assignment Tenant", slug="assignment-tenant")
    other = Organization.objects.create(name="Foreign Assignment Tenant", slug="foreign-assignment-tenant")
    Membership.objects.create(organization=org, user=member, role="MANAGER")
    Membership.objects.create(organization=other, user=foreign, role="EMPLOYEE")
    client = APIClient()
    client.force_authenticate(member)
    project_response = client.post(
        "/api/v1/delivery/projects/",
        {"name": "Cross-tenant manager", "service_line": "SOFTWARE", "project_manager": str(foreign.id)},
        format="json", HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert project_response.status_code == 400
    project = Project.objects.create(organization=org, name="Local project", service_line="SOFTWARE")
    task_response = client.post(
        "/api/v1/delivery/tasks/",
        {"project": str(project.id), "title": "Cross-tenant assignee", "assignee": str(foreign.id)},
        format="json", HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert task_response.status_code == 400
    assert not Task.objects.filter(organization=org).exists()
