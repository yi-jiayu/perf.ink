FROM python:3.10 as builder

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -

COPY pyproject.toml poetry.lock poetry.toml /workspace/
WORKDIR /workspace
RUN ["/etc/poetry/bin/poetry", "install", "--no-root", "--without=dev"]

FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /workspace/.venv /workspace/.venv
COPY . /workspace/

WORKDIR /workspace
ENV PATH="/workspace/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" app \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" app

USER app
