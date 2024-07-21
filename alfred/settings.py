import os

import structlog
from corsheaders.defaults import default_headers

from .config.globals import BASE_DIR
from .utils import flatten_list, read_env_var

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = read_env_var("DJANGO_SECRET_KEY")

# aws SES access
AWS_SES_ACCESS_KEY_ID = read_env_var("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = read_env_var("AWS_SES_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = read_env_var("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
AWS_SES_FROM_EMAIL = read_env_var("AWS_SES_FROM_EMAIL")
USE_SES_V2 = True

DOMAIN = read_env_var("DOMAIN")
SITE_NAME = read_env_var("SITE_NAME")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = read_env_var("DEBUG")

ALLOWED_HOSTS = read_env_var("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_structlog",
    "corsheaders",
    "rest_framework",
    "djoser",
    "users",
    "data",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "alfred.middleware.PartitionedCookieMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "alfred.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "alfred.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}


# Email settings
EMAIL_BACKEND = "django_ses.SESBackend"
DEFULT_FROM_EMAIL = AWS_SES_FROM_EMAIL

AUTH_USER_MODEL = "users.AlfredUser"
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

# rest framework
# https://www.django-rest-framework.org
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.AlfredJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
# djoser settings https://djoser.readthedocs.io/en/latest/settings.html
DJOSER = {
    "LOGIN_FIELD": "email",
    "PASSWORD_RESET_CONFIRM_URL": "password-reset/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "ACTIVATION_URL": "activation/{uid}/{token}",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "TOKEN_MODEL": None,
    "SERIALIZERS": {
        "user_create": "users.serializers.AlfredUserCreateSerializer",
        "user": "users.serializers.AlfredUserSerializer",
        "current_user": "users.serializers.AlfredUserSerializer",
    },
}

AUTH_COOKIE = "access"
AUTH_COOKIE_REFRESH = "refresh"
AUTH_COOKIE_ACCESS_MAX_AGE = 60 * 30  # half an hour
AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 * 24 * 45  # 45 days
AUTH_COOKIE_SECURE = True
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = "/"
AUTH_COOKIE_SAMESITE = "None"

# default jwt settings https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
# SIMPLE_JWT = {}

# corsheaders allowed
CORS_ALLOWED_ORIGINS = read_env_var("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_HEADERS = list(default_headers) + flatten_list(
    [read_env_var("CORS_ALLOWED_HEADERS")],
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = read_env_var("CSRF_TRUSTED_ORIGINS")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SPECTACULAR_SETTINGS = {
    "TITLE": "Alfred API",
    "DESCRIPTION": "API documentation for our app",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "json_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": "logs/json.log",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["console", "json_file"],
            "level": "DEBUG",
        },
        "root": {
            "handlers": ["console", "json_file"],
            "level": "DEBUG",
        },
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# ensure that json logs have their output
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
