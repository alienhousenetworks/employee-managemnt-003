from django.urls import path
from .views import (
    ClientListCreateView, ProjectListCreateView, TaskListCreateView, ServiceTemplateListCreateView, OpportunityListCreateView, ClientRenewalListCreateView, GitHubRepositoryLinkListCreateView, GitHubWorkItemLinkListCreateView,
    TaskDependencyListCreateView, ProjectDeliverableListCreateView, DeliverableTransitionView,
)
urlpatterns = [
    path("clients/", ClientListCreateView.as_view(), name="clients"),
    path("service-templates/", ServiceTemplateListCreateView.as_view(), name="service-templates"),
    path("opportunities/", OpportunityListCreateView.as_view(), name="opportunities"),
    path("renewals/", ClientRenewalListCreateView.as_view(), name="client-renewals"),
    path("github/repositories/", GitHubRepositoryLinkListCreateView.as_view(), name="github-repositories"),
    path("github/work-items/", GitHubWorkItemLinkListCreateView.as_view(), name="github-work-items"),
    path("projects/", ProjectListCreateView.as_view(), name="projects"),
    path("tasks/", TaskListCreateView.as_view(), name="tasks"),
    path("task-dependencies/", TaskDependencyListCreateView.as_view(), name="task-dependencies"),
    path("deliverables/", ProjectDeliverableListCreateView.as_view(), name="project-deliverables"),
    path("deliverables/<uuid:deliverable_id>/transition/", DeliverableTransitionView.as_view(), name="deliverable-transition"),
]
