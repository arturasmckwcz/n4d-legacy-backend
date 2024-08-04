from django.urls import path

from data.views import DataOpportunityListView, DataPersonView

urlpatterns = [
    path("me/", DataPersonView.as_view()),
    path("opportunity/", DataOpportunityListView.as_view()),
]
