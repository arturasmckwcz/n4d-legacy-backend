#!/bin/bash

source .venv/bin/activate

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

export ENV="TEST"
export DEBUG="True"

docker compose -p batman -f docker-compose.e2e.yaml up --force-recreate -V &

sleep 15

docker exec alfred python3 manage.py seed_data
docker exec alfred python3 manage.py loaddata data/fixtures/activities.json 
docker exec alfred python3 manage.py loaddata data/fixtures/berlinlocations.json
docker exec alfred python3 manage.py loaddata data/fixtures/need4deeddayschedule.json
docker exec alfred python3 manage.py loaddata data/fixtures/skills.json
docker exec alfred python3 manage.py loaddata data/fixtures/opportunities.json

PYTEST_DISABLE_PLUGIN_AUTOLOAD=True ALFRED_API_URL=http://localhost:8000 python3 -m pytest tests_e2e/test_endpoints/test_api_opportunity.py

docker compose -p batman -f docker-compose.dev.yaml down
