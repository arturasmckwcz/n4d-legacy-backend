from http import HTTPStatus

import structlog
from django.conf import settings
from rest_framework import status  # TODO: figure if it does the same as HTTPStatus
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from alfred.utils import AlfredRequest, AlfredResponse
from users.serializers import GroupSerializer

logger = structlog.get_logger(__name__)


class AlfredTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = AlfredResponse(super().post(request, *args, **kwargs))

        if response.status_code == HTTPStatus.OK:
            access_token = response.get_data_attr(key="access")
            refresh_token = response.get_data_attr(key="refresh")

            response.set_cookie(
                settings.AUTH_COOKIE,
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )

            response.set_cookie(
                settings.AUTH_COOKIE_REFRESH,
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )
        logger.debug(f"Set cookie {response=}")
        return response


class AlfredTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request = AlfredRequest(request)

        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if refresh_token:
            request.set_data_attr(key="refresh", value=refresh_token)

        response = AlfredResponse(super().post(request, *args, **kwargs))

        if response.status_code == HTTPStatus.OK:
            access_token = response.get_data_attr(key="access")

            response.set_cookie(
                settings.AUTH_COOKIE,
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )

        logger.debug(f"Refresh cookie {response=}")
        return response


class AlfredTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        request = AlfredRequest(request)

        access_token = request.COOKIES.get(settings.AUTH_COOKIE)

        if access_token:
            request.set_data_attr(key="token", value=access_token)

        logger.debug(f"Verify view {request}")
        return super().post(request, *args, **kwargs)


class AlfredLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.AUTH_COOKIE)
        response.delete_cookie(settings.AUTH_COOKIE_REFRESH)

        logger.debug(f"Logout view {response=}")
        return response


class AlfredUserGoupsView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        groups = user.groups.all()
        if len(groups) == 0:
            groups = [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}]

        serializer = GroupSerializer(groups, many=True)
        logger.debug(f"User groups {groups=}")
        return Response(serializer.data)
