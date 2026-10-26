from django.urls import path
from .views import EODListCreateView, EODSubmitView, EODReviewView
urlpatterns = [
    path("reports/", EODListCreateView.as_view(), name="eod-reports"),
    path("reports/<uuid:report_id>/submit/", EODSubmitView.as_view(), name="eod-submit"),
    path("reports/<uuid:report_id>/review/", EODReviewView.as_view(), name="eod-review"),
]
