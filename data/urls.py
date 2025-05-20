from django.urls import path

from data.views import (
    AuthEmailDomainView,
    DataOpportunityListView,
    DataPersonView,
    EventListView,
    TestimonialListView,
    VolunteerFormCreateView,
)

urlpatterns = [
    path("me/", DataPersonView.as_view()),
    path("opportunity/", DataOpportunityListView.as_view()),
    path("auth-email-domain/", AuthEmailDomainView.as_view()),
    path("testimonial/", TestimonialListView.as_view()),
    path("volunteer/", VolunteerFormCreateView().as_view()),
    path("event/", EventListView().as_view()),
]
