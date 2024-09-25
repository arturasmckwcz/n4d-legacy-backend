#!/bin/bash

source .venv/bin/activate

if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

docker compose -p batman down -v --remove-orphans

docker volume prune -f

docker builder prune -af

docker images | grep -E 'alfred|<none>' | awk '{print $3}' | xargs -r docker rmi -f

docker compose -p batman -f docker-compose.dev.yaml up
