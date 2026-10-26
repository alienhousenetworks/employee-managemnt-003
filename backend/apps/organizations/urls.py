from django.urls import path
from .views import MyOrganizationsView
urlpatterns = [path("mine/", MyOrganizationsView.as_view(), name="my-organizations")]
