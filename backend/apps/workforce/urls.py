from django.urls import path
from .views import EmployeeDirectoryView
urlpatterns = [path("", EmployeeDirectoryView.as_view(), name="employee-directory")]
