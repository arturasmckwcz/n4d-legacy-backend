from django.core.management.utils import get_random_secret_key

defaults = {
    "ENVIRONMENT": "production",
    "DJANGO_SECRET_KEY": get_random_secret_key(),
    "ALLOWED_HOSTS": [
        "127.0.0.1",
        "localhost",
        "192.168.0.124",
        "192.168.178.69",
        "api",
    ],
    "CORS_ALLOWED_ORIGINS": [
        "http://localhost:5500",
        "http://localhost:5174",
        "http://192.168.0.124:3080",
        "http://192.168.178.69:3080",
    ],
    "DOMAIN": "192.168.0.124:3080",
}
