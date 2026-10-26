from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import AttendanceEntry, LeaveRequest, EmployeeRequest
from .serializers import AttendanceSerializer, LeaveRequestSerializer, EmployeeRequestSerializer

class MyAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self): return AttendanceEntry.objects.filter(organization=self.request.organization, employee=self.request.user).order_by("-started_at")[:100]

class AttendanceActionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request):
        action = request.data.get("action")
        open_entry = AttendanceEntry.objects.select_for_update().filter(organization=request.organization, employee=request.user, status=AttendanceEntry.Status.OPEN).first()
        if action == "check_in":
            if open_entry: raise ValidationError({"attendance":"You already have an open attendance entry."})
            entry = AttendanceEntry.objects.create(organization=request.organization, employee=request.user, note=str(request.data.get("note", ""))[:500])
            return Response(AttendanceSerializer(entry).data, status=status.HTTP_201_CREATED)
        if action == "check_out":
            if not open_entry: raise ValidationError({"attendance":"No open attendance entry exists."})
            open_entry.ended_at = timezone.now(); open_entry.status = AttendanceEntry.Status.CLOSED
            open_entry.save(update_fields=["ended_at", "status"])
            return Response(AttendanceSerializer(open_entry).data)
        raise ValidationError({"action":"Use check_in or check_out."})

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = LeaveRequest.objects.filter(organization=self.request.organization)
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}: qs = qs.filter(employee=self.request.user)
        return qs
    def perform_create(self, serializer): serializer.save(organization=self.request.organization, employee=self.request.user)

class LeaveDecisionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request, leave_id):
        if request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}: raise PermissionDenied("Leave review permission is required.")
        leave = LeaveRequest.objects.select_for_update().filter(id=leave_id, organization=request.organization).first()
        if not leave: return Response({"detail":"Not found."}, status=404)
        decision = request.data.get("decision")
        if leave.status != LeaveRequest.Status.SUBMITTED: raise ValidationError({"status":"Only submitted leave requests can be reviewed."})
        if decision not in {"approve", "reject"}: raise ValidationError({"decision":"Use approve or reject."})
        leave.status = LeaveRequest.Status.APPROVED if decision == "approve" else LeaveRequest.Status.REJECTED
        leave.reviewer = request.user; leave.review_note = str(request.data.get("note", ""))[:3000]
        leave.save(update_fields=["status", "reviewer", "review_note", "updated_at"])
        return Response(LeaveRequestSerializer(leave).data)

class EmployeeRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeRequestSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self): return EmployeeRequest.objects.filter(organization=self.request.organization, employee=self.request.user).order_by("-created_at")
    def perform_create(self, serializer): serializer.save(organization=self.request.organization, employee=self.request.user)

from .models import ShiftSchedule, LeaveBalance
from .serializers import ShiftScheduleSerializer, LeaveBalanceSerializer

class ShiftScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = ShiftScheduleSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = ShiftSchedule.objects.filter(organization=self.request.organization).select_related("employee")
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            qs = qs.filter(employee=self.request.user)
        return qs.order_by("shift_date", "starts_at")
    def perform_create(self, serializer):
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            raise PermissionDenied("Only HR or managers can schedule shifts.")
        employee = serializer.validated_data["employee"]
        from apps.organizations.models import Membership
        if not Membership.objects.filter(organization=self.request.organization, user=employee, is_active=True).exists():
            raise ValidationError({"employee": "Employee must be an active member of this organization."})
        if serializer.validated_data["ends_at"] <= serializer.validated_data["starts_at"]:
            raise ValidationError({"ends_at": "Shift end must be after shift start on the same date."})
        serializer.save(organization=self.request.organization, created_by=self.request.user)

class MyLeaveBalanceListView(generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return LeaveBalance.objects.filter(organization=self.request.organization, employee=self.request.user).order_by("leave_type", "-period_start")

from .models import AttendanceCorrectionRequest, Candidate
from .serializers import AttendanceCorrectionSerializer, CandidateSerializer

class AttendanceCorrectionListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceCorrectionSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = AttendanceCorrectionRequest.objects.filter(organization=self.request.organization).select_related("attendance", "employee", "reviewed_by")
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            qs = qs.filter(employee=self.request.user)
        return qs.order_by("-created_at")
    def perform_create(self, serializer):
        attendance = serializer.validated_data["attendance"]
        if attendance.organization_id != self.request.organization.id or attendance.employee_id != self.request.user.id:
            raise ValidationError({"attendance": "Corrections can only be requested for your own attendance in this organization."})
        if not serializer.validated_data.get("reason", "").strip():
            raise ValidationError({"reason": "A correction reason is required."})
        serializer.save(organization=self.request.organization, employee=self.request.user)

class AttendanceCorrectionDecisionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    @transaction.atomic
    def post(self, request, correction_id):
        if request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            raise PermissionDenied("Attendance correction review permission is required.")
        correction = AttendanceCorrectionRequest.objects.select_for_update().filter(id=correction_id, organization=request.organization).first()
        if not correction:
            return Response({"detail": "Not found."}, status=404)
        if correction.status != AttendanceCorrectionRequest.Status.SUBMITTED:
            raise ValidationError({"status": "Only submitted corrections can be reviewed."})
        decision = request.data.get("decision")
        if decision not in {"approve", "reject"}:
            raise ValidationError({"decision": "Use approve or reject."})
        note = str(request.data.get("note", ""))[:2000]
        if decision == "approve":
            entry = correction.attendance
            if correction.proposed_start:
                entry.started_at = correction.proposed_start
            if correction.proposed_end:
                entry.ended_at = correction.proposed_end
            if entry.ended_at and entry.ended_at <= entry.started_at:
                raise ValidationError({"attendance": "Corrected end must be after start."})
            entry.status = AttendanceEntry.Status.APPROVED
            entry.save(update_fields=["started_at", "ended_at", "status"])
            correction.status = AttendanceCorrectionRequest.Status.APPROVED
        else:
            correction.status = AttendanceCorrectionRequest.Status.REJECTED
        correction.reviewed_by = request.user
        correction.review_note = note
        correction.reviewed_at = timezone.now()
        correction.save(update_fields=["status", "reviewed_by", "review_note", "reviewed_at"])
        return Response(AttendanceCorrectionSerializer(correction).data)

class CandidateListCreateView(generics.ListCreateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def _require_hr(self):
        if self.request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            raise PermissionDenied("Recruitment records are restricted to HR and managers.")
    def get_queryset(self):
        self._require_hr()
        return Candidate.objects.filter(organization=self.request.organization).order_by("-created_at")
    def perform_create(self, serializer):
        self._require_hr()
        owner = serializer.validated_data.get("owner")
        if owner and not self.request.organization.memberships.filter(user=owner, is_active=True).exists():
            raise ValidationError({"owner": "Candidate owner must belong to the active organization."})
        serializer.save(organization=self.request.organization)

class CandidateStageView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, candidate_id):
        if request.membership.role not in {"OWNER", "ADMIN", "HR", "MANAGER"}:
            raise PermissionDenied("Recruitment stage changes are restricted to HR and managers.")
        candidate = Candidate.objects.filter(id=candidate_id, organization=request.organization).first()
        if not candidate:
            return Response({"detail": "Not found."}, status=404)
        stage = request.data.get("stage")
        allowed = {choice for choice, _label in Candidate.Stage.choices}
        if stage not in allowed:
            raise ValidationError({"stage": "Unknown recruitment stage."})
        candidate.stage = stage
        candidate.save(update_fields=["stage", "updated_at"])
        return Response(CandidateSerializer(candidate).data)
