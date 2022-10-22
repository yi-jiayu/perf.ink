FROM python:3.10 as builder

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock poetry.toml /app/
RUN ["/etc/poetry/bin/poetry", "install", "--no-root", "--without=dev"]

FROM python:3.10-slim as app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY template.env /app/.env
COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

RUN ["python", "manage.py", "collectstatic", "--noinput"]

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" app \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" app

USER app
