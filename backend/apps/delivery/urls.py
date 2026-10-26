from django.urls import path
from .views import ClientListCreateView, ProjectListCreateView, TaskListCreateView
urlpatterns = [path("clients/", ClientListCreateView.as_view(), name="clients"), path("projects/", ProjectListCreateView.as_view(), name="projects"), path("tasks/", TaskListCreateView.as_view(), name="tasks")]
