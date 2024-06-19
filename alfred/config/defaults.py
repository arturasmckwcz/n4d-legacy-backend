from django.core.management.utils import get_random_secret_key

defaults = {
    "ENVIRONMENT": "production",
    "DJANGO_SECRET_KEY": get_random_secret_key(),
    "ALLOWED_HOSTS": [
        "127.0.0.1",
        "localhost",
        "192.168.0.124",
        "192.168.1.144",
        "192.168.178.69",
        "api",
    ],
    "CORS_ALLOWED_ORIGINS": [
        "http://localhost:3080",
        "http://192.168.0.124:3080",
        "http://192.168.0.124:8080",
        "http://192.168.0.124:8443",
        "http://192.168.1.144:3080",
        "http://192.168.1.144:8080",
        "https://192.168.1.144:8443",
        "http://192.168.178.69:3080",
        "http://192.168.178.69:8080",
        "http://192.168.178.69:8443",
    ],
    "CORS_ALLOWED_HEADERS": [
        "X-Requested-From",
    ],
    "CSRF_TRUSTED_ORIGINS": [
        "http://192.168.0.124:8080",
        "https://192.168.0.124:8443",
        "http://192.168.1.144:8080",
        "https://192.168.1.144:8443",
        "http://192.168.178.69:8080",
        "https://192.168.178.69:8443",
    ],
    "DOMAIN": "192.168.0.124:3080",
}
