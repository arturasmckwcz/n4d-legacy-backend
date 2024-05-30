## Development

#### How to start django

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
