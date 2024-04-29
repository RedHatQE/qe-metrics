FROM docker.io/library/python:3.12-slim

ENV POETRY_HOME=/qe-metrics

COPY pyproject.toml poetry.lock /qe-metrics/
COPY qe_metrics /qe-metrics/qe_metrics
WORKDIR /qe-metrics

RUN python3 -m pip install pip poetry --upgrade \
    && poetry config cache-dir /qe-metrics \
    && poetry config virtualenvs.in-project true \
    && poetry config installer.max-workers 10 \
    && poetry install

ENTRYPOINT ["poetry", "run", "qe-metrics"]
