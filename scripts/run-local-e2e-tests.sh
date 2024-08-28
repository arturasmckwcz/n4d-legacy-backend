#!/bin/bash

source .venv/bin/activate

if [ -f .env.local ]; then
    set -a
    . .env.local
    set +a
fi

API_PORT_NON_TLS=8080 API_PORT=8443 docker compose -p batman -f docker-compose.dev.yaml up --force-recreate -V &

sleep 15

docker exec alfred python3 manage.py seed_data

PYTEST_DISABLE_PLUGIN_AUTOLOAD=True ALFRED_API_URL=http://localhost:8000 python3 -m pytest tests_e2e

docker compose -p batman -f docker-compose.dev.yaml down
