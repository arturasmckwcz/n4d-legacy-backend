from datetime import timedelta
from http import HTTPStatus

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status  # TODO: figure if it does the same as HTTPStatus
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.serializers import GroupSerializer
from users.utils import AlfredRequest, AlfredResponse


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

        return response


class AlfredTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        request = AlfredRequest(request)

        access_token = request.COOKIES.get(settings.AUTH_COOKIE)

        if access_token:
            request.set_data_attr(key="token", value=access_token)

        return super().post(request, *args, **kwargs)


class AlfredLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.AUTH_COOKIE)
        response.delete_cookie(settings.AUTH_COOKIE_REFRESH)

        return response


class AlfredUserGoupsView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        groups = user.groups.all()
        if len(groups) == 0:
            groups = [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}]

        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class AlfredUserQuoteView(APIView):
    timer = {"last_time": timezone.now()}
    fallback_quote = "<blockquote>&ldquo;You don't have to move mountains. You'll change the world simply by being a warm, kind-hearted human being.&rdquo; &mdash; <footer>Anita Krizzan</footer></blockquote>"
    quote_response = {"quote": fallback_quote}

    def get(self, request):
        try:
            time_now = timezone.now()
            if time_now >= self.timer["last_time"] + timedelta(days=1):
                self.timer["last_time"] = time_now
                response = requests.get("https://zenquotes.io/api/random")
                response.raise_for_status()  # Raise an HTTPError on bad status
                data = response.json()
                if data and isinstance(data, list) and "h" in data[0]:
                    quote = data[0]["h"]
                    self.quote_response["quote"] = quote
            return Response(self.quote_response, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
