#!/bin/sh

python manage.py migrate
python manage.py loaddata data/fixtures/berlinlocations.json
python manage.py loaddata data/fixtures/activities.json
python manage.py loaddata data/fixtures/skills.json
python manage.py loaddata data/fixtures/leads.json
python manage.py load_test_data
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
