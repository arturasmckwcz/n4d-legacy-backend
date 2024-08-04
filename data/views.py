import structlog
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Opportunity
from data.serializers import OpportunitySerializer, PersonSerializer

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
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
