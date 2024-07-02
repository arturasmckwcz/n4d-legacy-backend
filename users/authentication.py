import structlog
from django.conf import settings
from rest_framework.views import Request
from rest_framework_simplejwt.authentication import AuthUser, JWTAuthentication
from rest_framework_simplejwt.tokens import Token

logger = structlog.get_logger(__name__)


class AlfredJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> tuple[AuthUser, Token] | None:
        try:
            header = self.get_header(request)
            logger.debug(f"JWT {header=}")
            if header is None:
                raw_token = request.COOKIES.get(settings.AUTH_COOKIE)
            else:
                raw_token = self.get_raw_token(header)

            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)

            return self.get_user(validated_token), validated_token
        except:  # noqa: E722
            logger.error("Error at alfred jwt auth")
            return None
