#!/bin/sh
python manage.py migrate
python manage.py flush_language
python manage.py loaddata data/fixtures/languages.json
python manage.py collectstatic --noinput
gunicorn --worker-class gevent --bind 0.0.0.0:8000 --forwarded-allow-ips='*' alfred.wsgi:application
