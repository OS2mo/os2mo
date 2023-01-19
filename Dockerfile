FROM python:3.10

# Main program
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN pip install --no-cache-dir poetry==1.2.2

WORKDIR /opt
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

WORKDIR /opt/app
COPY mo_ldap_import_export .
WORKDIR /opt/


# Cron
RUN apt-get update
RUN apt-get install -y curl jq
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.0/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=1f187c07bd973ff1cf5097a8caacbd1686ece5f1
RUN curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
 && chmod +x "$SUPERCRONIC" \
 && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
 && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic
COPY ./cron /cron
RUN chmod -R 100 "/cron/import_all.sh"
RUN chmod -R 400 "/cron/crontab"



# Default command
CMD [ "uvicorn", "--factory", "app.main:create_app", "--host", "0.0.0.0" ]


# Add build version to the environment last to avoid build cache misses
ARG COMMIT_TAG
ARG COMMIT_SHA
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD} \
    COMMIT_SHA=${COMMIT_SHA}
