import json

import structlog
from django.db.models import Subquery
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from data.enums import OptionsList
from data.models import (
    Activity,
    AuthEmailDomain,
    BerlinLocation,
    FormLeadFrom,
    Language,
    Opportunity,
    Skill,
)
from data.serializers import (
    OpportunityCreateSerializer,
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


class DataOpportunityListView(mixins.CreateModelMixin, ListAPIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60 * 45))  # 45 mins
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):  # type: ignore (asking for return type Never which is nonsense)
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
        context["language"] = self.request.GET.get("language", "de")
        try:
            primary_keys = json.loads(self.request.GET["primary_keys"])
        except json.JSONDecodeError:
            logger.warn("invalid primary_keys param value.")
            primary_keys = []
        except MultiValueDictKeyError:
            primary_keys = []
        context["primary_keys"] = primary_keys
        return context

    def get_serializer_class(self):  # type: ignore
        if self.request.method == "POST":
            return OpportunityCreateSerializer
        return OpportunitySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


def get_options_list(queryset, field):
    return [option[field] for option in queryset.values(field)]


def get_options_used_in_opportunities(model, field_name):
    objects = model.objects.filter(
        id__in=Subquery(Opportunity.objects.values(field_name))
    )

    return get_options_list(objects, "title")


class AuthEmailDomainView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        domain = request.GET.get("domain")

        result = AuthEmailDomain.objects.filter(domain=domain).first()
        return Response(result is not None)


class VolunteerFormCreateView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VolunteerFormSerializer

    @method_decorator(cache_page(60 * 60 * 48))  # bi-daily
    def get_options_lists(self, request):
        languages = get_options_used_in_opportunities(Language, "languages")
        locations = get_options_list(BerlinLocation.objects.all(), "name")
        activities = get_options_list(Activity.objects.all(), "title")
        skills = get_options_list(Skill.objects.all(), "title")
        leads = get_options_list(FormLeadFrom.objects.all(), "title")

        return {
            "lists": {
                OptionsList.LANGUAGES: languages,
                OptionsList.LOCATIONS: locations,
                OptionsList.ACTIVITIES: activities,
                OptionsList.SKILLS: skills,
                OptionsList.LEADS: leads,
            }
        }

    def options(self, request, *args, **kwargs):
        original_response = super().options(request, *args, **kwargs)

        cached_options = self.get_options_lists(request)

        if isinstance(original_response.data, dict):
            original_response.data.update(
                cached_options if isinstance(cached_options, dict) else {}
            )
        return original_response
