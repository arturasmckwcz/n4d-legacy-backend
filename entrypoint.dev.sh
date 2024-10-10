#!/bin/sh
python manage.py migrate
python manage.py flush_language
python manage.py loaddata data/fixtures/languages.json
python manage.py loaddata data/fixtures/berlinlocations.json
python manage.py loaddata data/fixtures/activities.json
python manage.py loaddata data/fixtures/skills.json
python manage.py loaddata data/fixtures/leads.json
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
