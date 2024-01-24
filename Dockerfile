FROM docker.io/library/python:3.11-slim

COPY pyproject.toml poetry.lock /qe-metrics/
COPY qe_metrics /qe-metrics/qe_metrics/
COPY --chmod=0755 dev /dev/

WORKDIR /qe-metrics

ENV POETRY_HOME=/qe-metrics
ENV PATH="/qe-metrics/bin:${PATH}"

RUN python3 -m pip install pip poetry --upgrade \
    && poetry config cache-dir /qe-metrics \
    && poetry config virtualenvs.in-project true \
    && poetry config installer.max-workers 10 \
    && poetry install \
    && apt update \
    && apt install -y --no-install-recommends vim nano

RUN printf '#!/bin/bash \n poetry run qe-metrics $@' > /usr/bin/qe-metrics \
    && chmod +x /usr/bin/qe-metrics

ENTRYPOINT qe-metrics
