from django.db import transaction
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
        qs = EODReport.objects.filter(organization=self.request.organization).prefetch_related("revisions")
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            qs = qs.filter(employee=self.request.user)
        return qs
    def perform_create(self, serializer):
        report = serializer.save(organization=self.request.organization, employee=self.request.user)
        EODRevision.objects.create(report=report, actor=self.request.user, new_status=report.status, note="Report draft created")

class EODSubmitView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request, report_id):
        report = EODReport.objects.select_for_update().filter(id=report_id, organization=request.organization).first()
        if not report:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if report.employee_id != request.user.id:
            raise PermissionDenied("Only the report owner may submit this report.")
        if report.status not in {EODReport.Status.DRAFT, EODReport.Status.NEEDS_CHANGES}:
            raise ValidationError({"status": "Only drafts or reports needing changes can be submitted."})
        previous = report.status
        report.status = EODReport.Status.SUBMITTED
        report.submitted_at = timezone.now()
        report.version += 1
        report.save(update_fields=["status", "submitted_at", "version", "updated_at"])
        EODRevision.objects.create(report=report, actor=request.user, previous_status=previous, new_status=report.status, note="Submitted by employee")
        return Response(EODReportSerializer(report).data)

class EODReviewView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request, report_id):
        if request.membership.role not in {"OWNER", "ADMIN", "MANAGER"}:
            raise PermissionDenied("EOD review permission is required.")
        report = EODReport.objects.select_for_update().filter(id=report_id, organization=request.organization).first()
        if not report:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        action = request.data.get("action")
        note = str(request.data.get("note", ""))[:4000]
        previous = report.status
        if action == "start_review" and report.status == EODReport.Status.SUBMITTED:
            report.status = EODReport.Status.IN_REVIEW
        elif action == "approve" and report.status == EODReport.Status.IN_REVIEW:
            report.status = EODReport.Status.APPROVED
        elif action == "needs_changes" and report.status == EODReport.Status.IN_REVIEW:
            if not note.strip():
                raise ValidationError({"note": "A review note is required when changes are requested."})
            report.status = EODReport.Status.NEEDS_CHANGES
        else:
            raise ValidationError({"action": "Allowed transitions: SUBMITTED → start_review → IN_REVIEW → approve or needs_changes."})
        report.reviewed_by = request.user
        report.review_note = note
        report.version += 1
        report.save(update_fields=["status", "reviewed_by", "review_note", "version", "updated_at"])
        EODRevision.objects.create(report=report, actor=request.user, previous_status=previous, new_status=report.status, note=note or action)
        return Response(EODReportSerializer(report).data)
