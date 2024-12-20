![coverage](https://gitlab.com/need4deed/alfred/badges/main/coverage.svg)

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

DEBUG="`true` for dev keep it in `.local.env` otherwise defaults to `false`"

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

2. run containers on default ports (8080 not TLS and 8443 with TLS):

```
docker compose -p batman -f docker-compose.dev.yaml up
```

3. also you may run on other ports:

```
API_PORT_NON_TLS=8080 API_PORT=8443 docker compose -p batman -f docker-compose.dev.yaml up
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

### Run books

# How to:

_Add another project files to the CI/CD pipeline of this project?_

Go to the another project -> Settings -> CI/CD -> Job token permissions
Add this group/project to the allowlist
Use CI_JOB_TOKEN in this project

### Loading opportunities as `json` file

#### Endpoit

```
/api/opportunities.json/
```

takes form field of type `file` named `json_file`

#### File format

Please check [the test file](./tests_e2e/fixtures/opportunities.json) as example
It should be an array of objects
Each object should correspond to the following OTD:

```
{
    "Status": "opportunity.status",
    "Name": "opportunity.title",
    "Type": "payload.activities",
    "District": "payload.locations",
    "Number of volunteers needed": "opportunity.volunteers_number",
    "Schedule": "payload.timeslots",
    "Accommodation Centre": "opportunity.organization",
    "Languages needed": "payload.languages",
    "Target group": "opportunity.target_groups",
    "VO information": "opportunity.vo_information",
    "ID": "opportunity.notion_id",

}
```

#### How to create test data:

Go to a working pod and dump data
python manage.py dumpdata --format json --indent 4 data.Opportunity > opportunities.json
python manage.py dumpdata --format json --indent 4 data.OpportunityTranslation > opportunity_translations.json
python manage.py dumpdata data.TargetGroup > targetgroup.json
python manage.py dumpdata data.TimeSlot > timeslots.json
python manage.py dumpdata data.BerlinLocation > berlinlocations.json
python manage.py dumpdata data.Activity > activities.json
Copy to fixtures folder

Script to quickly export .env in the current shell
grep -v '^#' .env | while IFS='=' read -r key value; do export "$key"="$value"; done
