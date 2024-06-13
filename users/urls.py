from django.urls import path

from .views import (
    AlfredLogoutView,
    AlfredTokenObtainPairView,
    AlfredTokenRefreshView,
    AlfredTokenVerifyView,
    AlfredUserGoupsView,
)

urlpatterns = [
    path("jwt/create/", AlfredTokenObtainPairView.as_view()),
    path("jwt/refresh/", AlfredTokenRefreshView.as_view()),
    path("jwt/verify/", AlfredTokenVerifyView.as_view()),
    path("user/logout/", AlfredLogoutView.as_view()),
    path("user/groups/", AlfredUserGoupsView.as_view()),
]
