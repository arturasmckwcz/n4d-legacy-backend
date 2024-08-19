from django.urls import path

from parse_opportunities.views import OpportunitiesJSONFileUploadView

urlpatterns = [
    path("opportunities.json/", OpportunitiesJSONFileUploadView.as_view()),
]
