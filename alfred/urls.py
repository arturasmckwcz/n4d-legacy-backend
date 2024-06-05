from django.contrib import admin
from django.urls import include, path

from .views import AlfredSanityView

urlpatterns = [
    path("sanity/", AlfredSanityView.as_view(), name="sanity"),
    path("admin/", admin.site.urls),
    path("api/", include("djoser.urls")),
    path("api/", include("users.urls")),
]
