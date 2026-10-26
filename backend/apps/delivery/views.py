from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import ClientAccount, Project, Task
from .serializers import ClientSerializer, ProjectSerializer, TaskSerializer

class TenantListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self): return self.model.objects.filter(organization=self.request.organization).order_by("-created_at")
    def perform_create(self, serializer): serializer.save(organization=self.request.organization, **self.create_defaults())
    def create_defaults(self): return {}
class ClientListCreateView(TenantListCreate):
    model = ClientAccount
    serializer_class = ClientSerializer
class ProjectListCreateView(TenantListCreate):
    model = Project
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        client = serializer.validated_data.get("client")
        if client and client.organization_id != self.request.organization.id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"client": "Client must belong to the active organization."})
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
