from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import EODReport, EODRevision
from .serializers import EODReportSerializer

class EODListCreateView(generics.ListCreateAPIView):
    serializer_class = EODReportSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = EODReport.objects.filter(organization=self.request.organization)
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            qs = qs.filter(employee=self.request.user)
        return qs
    def perform_create(self, serializer):
        report = serializer.save(organization=self.request.organization, employee=self.request.user)
        EODRevision.objects.create(report=report, actor=self.request.user, new_status=report.status, note="Report draft created")

class EODSubmitView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, report_id):
        report = EODReport.objects.filter(id=report_id, organization=request.organization).first()
        if not report: return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        if report.employee_id != request.user.id: raise PermissionDenied("Only the report owner may submit this report.")
        if report.status not in {EODReport.Status.DRAFT, EODReport.Status.NEEDS_CHANGES}: raise ValidationError({"status":"Only drafts or reports needing changes can be submitted."})
        previous = report.status
        report.status = EODReport.Status.SUBMITTED
        report.submitted_at = timezone.now()
        report.version += 1
        report.save(update_fields=["status", "submitted_at", "version", "updated_at"])
        EODRevision.objects.create(report=report, actor=request.user, previous_status=previous, new_status=report.status, note="Submitted by employee")
        return Response(EODReportSerializer(report).data)
