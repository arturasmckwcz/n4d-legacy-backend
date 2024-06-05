from http import HTTPStatus

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class AlfredSanityView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        return Response({"message": "OK"}, status=HTTPStatus.OK)
