FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app
COPY dev-requirements.txt /app
COPY tests_e2e /app/tests_e2e

RUN pip install --upgrade pip && pip install -r dev-requirements.txt

ENTRYPOINT ["python3", "-m", "pytest", "-vvv", "tests_e2e"]
