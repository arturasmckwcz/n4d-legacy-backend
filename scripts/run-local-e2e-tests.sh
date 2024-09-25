#!/bin/bash

source .venv/bin/activate

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

docker compose -p batman -f docker-compose.dev.yaml up --force-recreate -V &

sleep 15

docker exec alfred python3 manage.py seed_data
docker exec alfred python3 manage.py loaddata data/fixtures/targetgroup.json
docker exec alfred python3 manage.py loaddata data/fixtures/activities.json 
docker exec alfred python3 manage.py loaddata data/fixtures/berlinlocations.json
docker exec alfred python3 manage.py loaddata data/fixtures/timeslots.json
docker exec alfred python3 manage.py loaddata data/fixtures/opportunities.json

PYTEST_DISABLE_PLUGIN_AUTOLOAD=True ALFRED_API_URL=http://localhost:8000 python3 -m pytest tests_e2e

docker compose -p batman -f docker-compose.dev.yaml down
