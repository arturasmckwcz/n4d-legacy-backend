import structlog
from rest_framework.response import Response
from rest_framework.views import APIView

from data.serializers import DataPersonSerializer

logger = structlog.get_logger(__name__)


class DataPersonView(APIView):
    def get(self, request, *args, **kwargs):
        person = request.user.person

        serializer = DataPersonSerializer(person)
        response = Response(serializer.data)

        logger.debug(f"DataPersonView {response=}")
        return response
