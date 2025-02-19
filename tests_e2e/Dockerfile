FROM python:3.12-slim

ARG ALFRED_API_URL
ARG ENVIRONMENT
ENV ALFRED_API_URL=${ALFRED_API_URL}
ENV ENVIRONMENT=${ENVIRONMENT}

WORKDIR /app
COPY requirements.txt /app
COPY dev-requirements.txt /app
COPY tests_e2e /app/tests_e2e

RUN pip install --upgrade pip && pip install -r dev-requirements.txt

ENTRYPOINT ["python3", "-m", "pytest", "-vvvss", "tests_e2e"]
