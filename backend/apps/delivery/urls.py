from django.urls import path
from .views import (
    ClientListCreateView, ProjectListCreateView, TaskListCreateView,
    TaskDependencyListCreateView, ProjectDeliverableListCreateView, DeliverableTransitionView,
)
urlpatterns = [
    path("clients/", ClientListCreateView.as_view(), name="clients"),
    path("projects/", ProjectListCreateView.as_view(), name="projects"),
    path("tasks/", TaskListCreateView.as_view(), name="tasks"),
    path("task-dependencies/", TaskDependencyListCreateView.as_view(), name="task-dependencies"),
    path("deliverables/", ProjectDeliverableListCreateView.as_view(), name="project-deliverables"),
    path("deliverables/<uuid:deliverable_id>/transition/", DeliverableTransitionView.as_view(), name="deliverable-transition"),
]
