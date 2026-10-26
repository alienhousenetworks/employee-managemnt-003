from django.urls import path
from .views import MyAttendanceView, AttendanceActionView, LeaveRequestListCreateView, LeaveDecisionView, EmployeeRequestListCreateView
urlpatterns = [path("attendance/", MyAttendanceView.as_view(), name="my-attendance"), path("attendance/action/", AttendanceActionView.as_view(), name="attendance-action"), path("leave/", LeaveRequestListCreateView.as_view(), name="leave-requests"), path("leave/<uuid:leave_id>/decision/", LeaveDecisionView.as_view(), name="leave-decision"), path("requests/", EmployeeRequestListCreateView.as_view(), name="employee-requests")]
