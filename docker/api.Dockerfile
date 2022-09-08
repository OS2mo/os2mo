# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

FROM node:10 AS frontend

WORKDIR /app/frontend

COPY frontend/package.json .
COPY frontend/yarn.lock .
# We fail hard if the yaml.lock is outdated.
RUN yarn install --frozen-lockfile && yarn cache clean

COPY frontend .
RUN yarn build

# script for `vue-cli-service serve` from frontend/package.json
CMD ["yarn", "dev"]


FROM python:3.10 AS dist

LABEL org.opencontainers.image.title="OS2mo - Medarbejder og Organisation"
LABEL org.opencontainers.image.vendor="Magenta ApS"
LABEL org.opencontainers.image.licenses="MPL-2.0"
LABEL org.opencontainers.image.url="https://os2.eu/produkt/os2mo"
LABEL org.opencontainers.image.documentation="https://os2mo.readthedocs.io"
LABEL org.opencontainers.image.source="https://github.com/OS2mo/os2mo"

# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1

WORKDIR /app/
# hadolint ignore=DL3008,DL4006
RUN set -ex \
  # Add a mox group and user. Note: this is a system user/group, but have
  # UID/GID above the normal SYS_UID_MAX/SYS_GID_MAX of 999, but also above the
  # automatic ranges of UID_MAX/GID_MAX used by useradd/groupadd. See
  # `/etc/login.defs`. Hopefully there will be no conflicts with users of the
  # host system or users of other docker containers.
  #
  # See `doc/user/installation.rst` for instructions on how to overwrite this.
  && groupadd -g 72020 -r mora\
  && useradd -u 72020 --no-log-init -r -g mora mora \
  # Install dependencies
  && apt-get -y update \
  && apt-get -y install --no-install-recommends git \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf "/var/lib/apt/lists"

# Enviroment variables for poetry
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
  PYTHONPATH=/app:/app/backend \
  POETRY_VERSION="1.2.0" \
  POETRY_VIRTUALENVS_CREATE=true \
  POETRY_VIRTUALENVS_IN_PROJECT=true

# Install requirements
RUN pip3 install --no-cache-dir poetry==${POETRY_VERSION}
COPY backend/poetry.lock backend/pyproject.toml /app/backend/
WORKDIR /app/backend
RUN poetry install --no-interaction && rm -rf /root/.cache
WORKDIR /app

# Copy and install backend code.
COPY docker ./docker
COPY backend ./backend
COPY README.rst .
COPY NEWS.md .
COPY LICENSE .
COPY backend/mora/main.py .

# Copy frontend code.
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN install -g mora -o mora -d /log

# Run the server as the mora user on port 5000
USER mora:mora

VOLUME /queries

ENV ALEMBIC_CONFIG=/app/backend/alembic.ini

# Add build version to the environment last to avoid build cache misses
ARG COMMIT_TAG
ARG COMMIT_SHA
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD} \
    COMMIT_SHA=${COMMIT_SHA}

CMD ["./docker/start.sh"]
