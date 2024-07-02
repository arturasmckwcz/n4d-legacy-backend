from http import HTTPStatus

import structlog
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = structlog.get_logger(__name__)


class AlfredSanityView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        x_requested_from = request.headers.get("X-Requested-From")
        logger.debug(f"Sanity view {request=}")
        return Response(
            {"message": "OK", "x_requested_from": x_requested_from},
            status=HTTPStatus.OK,
        )
