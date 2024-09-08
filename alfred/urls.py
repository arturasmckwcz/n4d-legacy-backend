from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import AlfredSanityView

urlpatterns = [
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("sanity/", AlfredSanityView.as_view(), name="sanity"),
    path("admin/", admin.site.urls),
    path("api/", include("djoser.urls")),
    path("api/", include("users.urls")),
    path("api/", include("data.urls")),
    path("api/", include("parse_opportunities.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("silk/", include("silk.urls", namespace="silk")),
]
