from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.workforce.views import MeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/me/", MeView.as_view(), name="me"),
    path("api/v1/organizations/", include("apps.organizations.urls")),
    path("api/v1/employees/", include("apps.workforce.urls")),
    path("api/v1/feed/", include("apps.feed.urls")),
    path("api/v1/delivery/", include("apps.delivery.urls")),
    path("api/v1/eod/", include("apps.eod.urls")),
    path("api/v1/hr/", include("apps.hr.urls")),
    path("api/v1/approvals/", include("apps.approvals.urls")),
    path("api/v1/whatsapp/", include("apps.whatsapp.urls")),
]
