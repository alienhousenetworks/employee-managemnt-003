from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.organizations.models import Membership
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import EmployeeProfile
from .serializers import EmployeeProfileSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user, is_active=True, organization__is_active=True).select_related("organization")
        return Response({"id": str(request.user.pk), "username": request.user.get_username(), "email": request.user.email, "organizations": [{"id": str(m.organization_id), "name": m.organization.name, "role": m.role, "department": m.department} for m in memberships]})

class EmployeeDirectoryView(ListAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = EmployeeProfile.objects.filter(organization=self.request.organization, is_active=True).order_by("display_name")
        search = self.request.query_params.get("search", "").strip()
        department = self.request.query_params.get("department", "").strip()
        if search: qs = qs.filter(display_name__icontains=search) | qs.filter(employee_code__icontains=search)
        if department: qs = qs.filter(department=department)
        return qs
