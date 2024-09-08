from django.urls import path

from data.views import (
    DataOpportunityFlush,
    DataOpportunityListView,
    DataPersonView,
    VolunteerFormCreateView,
)

urlpatterns = [
    path("me/", DataPersonView.as_view()),
    path("opportunity/", DataOpportunityListView.as_view()),
    path("volunteer/", VolunteerFormCreateView().as_view()),
    path("opportunity/flush/", DataOpportunityFlush.as_view()),
]
