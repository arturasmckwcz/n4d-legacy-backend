## Development

#### How to start django
Ensure that you have env variables set.
`python manage.py runserver`

#### How to use uv

`https://github.com/astral-sh/uv`

#### To create a venv:

`uv venv`

#### To install packages:

`uv pip install`

#### The project uses uv's pip compile to manage the dependencies.

In your venv:

```
uv pip compile requirements.in -o requirements.txt
uv pip install -r requirements.txt
uv pip sync requirements.txt
```

#### To upgrade the packages:

`uv pip compile --upgrade requirements.in`

#### Run pre-commit

`pre-commit install`

update:
`pre-commit autoupdate`

#### How to use pyright

create local pyrightconfig.json

`cp pyrightconfig-ci.json pyrightconfig.json`
Find your venv path:

`echo $VIRTUAL_ENV`

add your own venv config (example):

```
"venvPath": "/home/alfred/",
"venv": ".venv"
```

Then execute

`pyright`

#### Requirements for environment vars

DJANGO_SECRET_KEY="any random string for dev only, keep it in `.local.env`"

DEBUG="`true` for dev keep it in `.local.env` othervise defaults to `false`"

AWS_SES_ACCESS_KEY_ID=

AWS_SES_SECRET_ACCESS_KEY=

AWS_SES_REGION_NAME=

AWS_SES_FROM_EMAIL=

DOMAIN="frontend domain used in email templates"

SITE_NAME="used as a team name in email templates"

#### HOW TO RUN THE PROJECT LOCALLY WITH DOCKER COMPOSE
```
docker compose --env-file .env.local -f docker-compose.dev.yaml up --build
```

#### HOW TO DEPLOY A DOCKER IMAGE TO Amazon ECR

Be sure that the env vars are set:
(e.g. GitLab CI/CD Environment Variables)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
ECR_REGISTRY
ECR_REPOSITORY

#### Dockerized

1. make sure you have got docker deamon up'n'running
2. make sure you have generated self signed certoificates for TLS:

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./nginx/cert/localhost.key -out ./nginx/cert/localhost.crt
```

3. run containers on default ports (8080 not TLS and 8443 with TLS):

```
docker compose -p batman -f docker-compose.dev.yml up
```

4. also you may run on other ports:

```
API_PORT_NON_TLS=8080 API_PORT=8443 docker compose -p batman -f docker-compose.dev.yml up
```

#### Local
0. cd to project dir
1. Quick way to export env vars
```
set -a && source .env && set +a
```
2. Activate venv
```
source .venv/bin/activate
```
2. Run
```
python3 manage.py runserver
```
