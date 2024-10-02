import json

import structlog
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from silk.profiling.profiler import silk_profile

from data.models import Opportunity
from data.serializers import (
    OpportunitySerializer,
    PersonSerializer,
    VolunteerFormSerializer,
)
from data.utils import filter_queryset

logger = structlog.get_logger(__name__)


class DataPersonView(APIView):
    def get(self, request, *args, **kwargs):
        person = request.user.person

        serializer = PersonSerializer(person)
        response = Response(serializer.data)

        logger.debug(f"DataPersonView {response=}")
        return response


class DataOpportunityListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = OpportunitySerializer

    @method_decorator(cache_page(60 * 45))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @silk_profile(name="Post Profiling")
    def get_queryset(self):  # type: ignore (askinkg for return type Never which is nonsense)
        try:
            filter_dict = json.loads(self.request.GET["search"])
        except json.JSONDecodeError:
            logger.warn("invalid search param value.")
            filter_dict = {}
        except MultiValueDictKeyError:
            logger.warn("missing search param.")
            filter_dict = {}
        opportunities = Opportunity.objects.filter()
        return filter_queryset(opportunities, filter_dict)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            primary_keys = json.loads(self.request.GET["primary_keys"])
        except json.JSONDecodeError:
            logger.warn("invalid primary_keys param value.")
            primary_keys = []
        except MultiValueDictKeyError:
            primary_keys = []
        context["primary_keys"] = primary_keys
        return context


class VolunteerFormCreateView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VolunteerFormSerializer
