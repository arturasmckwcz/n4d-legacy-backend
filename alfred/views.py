from http import HTTPStatus

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class AlfredSanityView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        x_requested_from = request.headers.get("X-Requested-From")
        return Response(
            {"message": "OK", "x_requested_from": x_requested_from},
            status=HTTPStatus.OK,
        )
