from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import ClientAccount, Project, Task, TaskDependency, ProjectDeliverable
from .serializers import ClientSerializer, ProjectSerializer, TaskSerializer, TaskDependencySerializer, ProjectDeliverableSerializer

class TenantListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self): return self.model.objects.filter(organization=self.request.organization).order_by("-created_at")
    def perform_create(self, serializer): serializer.save(organization=self.request.organization, **self.create_defaults())
    def create_defaults(self): return {}
class ClientListCreateView(TenantListCreate):
    model = ClientAccount
    serializer_class = ClientSerializer
    def perform_create(self, serializer):
        owner = serializer.validated_data.get("account_owner")
        if owner and not self.request.organization.memberships.filter(user=owner, is_active=True).exists():
            raise ValidationError({"account_owner": "Client owner must belong to the active organization."})
        super().perform_create(serializer)
class ProjectListCreateView(TenantListCreate):
    model = Project
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        client = serializer.validated_data.get("client")
        if client and client.organization_id != self.request.organization.id:
            raise ValidationError({"client": "Client must belong to the active organization."})
        manager = serializer.validated_data.get("project_manager")
        if manager and not self.request.organization.memberships.filter(user=manager, is_active=True).exists():
            raise ValidationError({"project_manager": "Project manager must belong to the active organization."})
        super().perform_create(serializer)
class TaskListCreateView(TenantListCreate):
    model = Task
    serializer_class = TaskSerializer
    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.organization_id != self.request.organization.id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"project": "Project must belong to the active organization."})
        serializer.save(organization=self.request.organization, created_by=self.request.user)

class TaskDependencyListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskDependencySerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return TaskDependency.objects.filter(organization=self.request.organization).select_related("predecessor", "successor").order_by("-created_at")
    def perform_create(self, serializer):
        predecessor = serializer.validated_data["predecessor"]
        successor = serializer.validated_data["successor"]
        org_id = self.request.organization.id
        if predecessor.organization_id != org_id or successor.organization_id != org_id:
            raise ValidationError({"tasks": "Both tasks must belong to the active organization."})
        if predecessor.project_id != successor.project_id:
            raise ValidationError({"tasks": "Dependencies must connect tasks in the same project."})
        if predecessor.id == successor.id:
            raise ValidationError({"successor": "A task cannot depend on itself."})
        # Prevent cycles: a path from successor back to predecessor would make this edge cyclic.
        graph = {}
        for edge in TaskDependency.objects.filter(organization=self.request.organization).values_list("predecessor_id", "successor_id"):
            graph.setdefault(edge[0], set()).add(edge[1])
        pending, seen = [successor.id], set()
        while pending:
            node = pending.pop()
            if node == predecessor.id:
                raise ValidationError({"successor": "This dependency would create a cycle."})
            if node not in seen:
                seen.add(node)
                pending.extend(graph.get(node, set()) - seen)
        serializer.save(organization=self.request.organization, created_by=self.request.user)

class ProjectDeliverableListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectDeliverableSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = ProjectDeliverable.objects.filter(organization=self.request.organization).select_related("project", "created_by", "approved_by")
        project_id = self.request.query_params.get("project_id")
        return qs.filter(project_id=project_id) if project_id else qs
    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.organization_id != self.request.organization.id:
            raise ValidationError({"project": "Project must belong to the active organization."})
        assignee = serializer.validated_data.get("assignee")
        if assignee and not self.request.organization.memberships.filter(user=assignee, is_active=True).exists():
            raise ValidationError({"assignee": "Task assignee must belong to the active organization."})
        serializer.save(organization=self.request.organization, created_by=self.request.user)

class DeliverableTransitionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request, deliverable_id):
        deliverable = ProjectDeliverable.objects.select_for_update().filter(id=deliverable_id, organization=request.organization).first()
        if not deliverable:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        action = request.data.get("action")
        transitions = {
            "start": (ProjectDeliverable.Status.DRAFT, ProjectDeliverable.Status.IN_PROGRESS),
            "submit_qa": (None, ProjectDeliverable.Status.READY_FOR_QA),
            "qa_fail": (ProjectDeliverable.Status.READY_FOR_QA, ProjectDeliverable.Status.QA_FAILED),
            "qa_pass": (ProjectDeliverable.Status.READY_FOR_QA, ProjectDeliverable.Status.APPROVED),
            "deliver": (ProjectDeliverable.Status.APPROVED, ProjectDeliverable.Status.DELIVERED),
        }
        if action not in transitions:
            raise ValidationError({"action": "Use start, submit_qa, qa_fail, qa_pass or deliver."})
        expected, target = transitions[action]
        if action == "submit_qa":
            if deliverable.status not in {ProjectDeliverable.Status.IN_PROGRESS, ProjectDeliverable.Status.QA_FAILED}:
                raise ValidationError({"status": "Only in-progress or QA-failed deliverables can be submitted for QA."})
        elif deliverable.status != expected:
            raise ValidationError({"status": f"Action requires status {expected}."})
        if action in {"qa_pass", "qa_fail", "deliver"} and request.membership.role not in {"OWNER", "ADMIN", "MANAGER"}:
            raise PermissionDenied("QA and delivery decisions require a manager or administrator.")
        deliverable.status = target
        if action in {"qa_pass", "qa_fail"}:
            deliverable.qa_notes = str(request.data.get("note", ""))[:4000]
        if action == "qa_pass":
            deliverable.approved_by = request.user
        deliverable.version += 1
        deliverable.save(update_fields=["status", "qa_notes", "approved_by", "version", "updated_at"])
        return Response(ProjectDeliverableSerializer(deliverable).data)

from .models import ServiceTemplate, Opportunity, ClientRenewal, GitHubRepositoryLink, GitHubWorkItemLink
from .serializers import ServiceTemplateSerializer, OpportunitySerializer, ClientRenewalSerializer, GitHubRepositoryLinkSerializer, GitHubWorkItemLinkSerializer

class ServiceTemplateListCreateView(TenantListCreate):
    model = ServiceTemplate
    serializer_class = ServiceTemplateSerializer

class OpportunityListCreateView(TenantListCreate):
    model = Opportunity
    serializer_class = OpportunitySerializer
    def perform_create(self, serializer):
        client = serializer.validated_data.get("client")
        if client and client.organization_id != self.request.organization.id:
            raise ValidationError({"client": "Client must belong to the active organization."})
        owner = serializer.validated_data.get("owner")
        if owner and not self.request.organization.memberships.filter(user=owner, is_active=True).exists():
            raise ValidationError({"owner": "Opportunity owner must belong to the active organization."})
        serializer.save(organization=self.request.organization)

class ClientRenewalListCreateView(TenantListCreate):
    model = ClientRenewal
    serializer_class = ClientRenewalSerializer
    def perform_create(self, serializer):
        values = serializer.validated_data
        if values["client"].organization_id != self.request.organization.id:
            raise ValidationError({"client": "Client must belong to the active organization."})
        project = values.get("project")
        if project and project.organization_id != self.request.organization.id:
            raise ValidationError({"project": "Project must belong to the active organization."})
        if project and project.client_id != values["client"].id:
            raise ValidationError({"project": "Renewal project must belong to the selected client."})
        owner = values.get("owner")
        if owner and not self.request.organization.memberships.filter(user=owner, is_active=True).exists():
            raise ValidationError({"owner": "Renewal owner must belong to the active organization."})
        serializer.save(organization=self.request.organization)

class GitHubRepositoryLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = GitHubRepositoryLinkSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return GitHubRepositoryLink.objects.filter(organization=self.request.organization).select_related("project")
    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.organization_id != self.request.organization.id:
            raise ValidationError({"project": "Project must belong to the active organization."})
        serializer.save(organization=self.request.organization)

class GitHubWorkItemLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = GitHubWorkItemLinkSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return GitHubWorkItemLink.objects.filter(organization=self.request.organization)
    def perform_create(self, serializer):
        task = serializer.validated_data["task"]
        repository = serializer.validated_data["repository"]
        if task.organization_id != self.request.organization.id:
            raise ValidationError({"task": "Task is outside the active organization."})
        if repository.organization_id != self.request.organization.id:
            raise ValidationError({"repository": "Repository is outside the active organization."})
        if task.project_id != repository.project_id:
            raise ValidationError({"task": "Task and repository must share a project."})
        serializer.save(organization=self.request.organization)
