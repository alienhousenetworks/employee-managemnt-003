from django.urls import path
from .views import ApprovalListCreateView, ApprovalDecisionView
urlpatterns = [path("", ApprovalListCreateView.as_view(), name="approvals"), path("<uuid:approval_id>/decision/", ApprovalDecisionView.as_view(), name="approval-decision")]
