from django.urls import path

from data.views import DataPersonView

urlpatterns = [
    path("me/", DataPersonView.as_view()),
]
