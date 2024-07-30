from http import HTTPStatus

import structlog
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from alfred.utils import read_env_var

logger = structlog.get_logger(__name__)


class AlfredSanityView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        x_requested_from = request.headers.get("X-Requested-From")
        logger.debug(f"Sanity view {request=}")

        last_commit = read_env_var("ALFRED_LAST_COMMIT_HASH", False)
        return Response(
            {
                "message": "OK",
                "x_requested_from": x_requested_from,
                "last_commit": last_commit,
            },
            status=HTTPStatus.OK,
        )
