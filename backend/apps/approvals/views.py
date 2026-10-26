from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer

class ApprovalListCreateView(generics.ListCreateAPIView):
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = ApprovalRequest.objects.filter(organization=self.request.organization)
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "FINANCE", "MANAGER"}:
            qs = qs.filter(requested_by=self.request.user)
        return qs.order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, requested_by=self.request.user)

class ApprovalDecisionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, approval_id):
        if request.membership.role not in {"OWNER", "ADMIN", "HR", "FINANCE", "MANAGER"}: raise PermissionDenied("Approval decision permission is required.")
        approval = ApprovalRequest.objects.filter(id=approval_id, organization=request.organization).first()
        if not approval: return Response({"detail":"Not found."}, status=404)
        if approval.status != ApprovalRequest.Status.PENDING: raise ValidationError({"status":"Only pending approvals can be decided."})
        decision = request.data.get("decision")
        if decision not in {"approve", "reject"}: raise ValidationError({"decision":"Use approve or reject."})
        approval.status = ApprovalRequest.Status.APPROVED if decision == "approve" else ApprovalRequest.Status.REJECTED
        approval.reviewer = request.user
        approval.decision_note = str(request.data.get("note", ""))[:4000]
        approval.decided_at = timezone.now()
        approval.save(update_fields=["status", "reviewer", "decision_note", "decided_at"])
        # Approval records the human decision; it deliberately does not execute the action.
        return Response(ApprovalRequestSerializer(approval).data)
