# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

FROM python:3.11@sha256:2e376990a11f1c1e03796d08db0e99c36eadb4bb6491372b227f1e53c3482914
ARG SOURCE_DATE_EPOCH

LABEL org.opencontainers.image.title="OS2mo - Medarbejder og Organisation"
LABEL org.opencontainers.image.vendor="Magenta ApS"
LABEL org.opencontainers.image.licenses="MPL-2.0"
LABEL org.opencontainers.image.url="https://os2.eu/produkt/os2mo"
LABEL org.opencontainers.image.documentation="https://os2mo.readthedocs.io"
LABEL org.opencontainers.image.source="https://github.com/OS2mo/os2mo"

# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # We don't install the backend as a package, so we add it to PYTHONPATH.
    PYTHONPATH=/app:/app/backend \
    POETRY_VERSION="1.3.2" \
    POETRY_HOME=/opt/poetry \
    ALEMBIC_CONFIG=/app/backend/alembic.ini

# https://www.redhat.com/en/blog/user-flag-rootless-containers:
#
# > The rootless Podman user is only allocated a limited number of {UID,GID}s, as
# > defined in the /etc/{subuid,subgid} files. Usually, you can only use 65536
# > {UID,GID}s. This means that if you attempt to launch a rootless container
# > with a {UID,GID} of > 65536, the container will fail.
#
# Ideally, we would change this, but prod deployments are hard to change and
# thus the default needs to stay at 72020. This allows the values to be
# overwritten in docker-compose for rootless podman development.
ARG uid=72020
ARG gid=72020

# hadolint ignore=DL3008,DL4006
RUN set -ex \
  # Add a mox group and user. Note: this is a system user/group, but have
  # UID/GID above the normal SYS_UID_MAX/SYS_GID_MAX of 999, but also above the
  # automatic ranges of UID_MAX/GID_MAX used by useradd/groupadd. See
  # `/etc/login.defs`. Hopefully there will be no conflicts with users of the
  # host system or users of other docker containers.
  #
  # See `doc/user/installation.rst` for instructions on how to overwrite this.
  && groupadd -g $gid -r mora\
  && useradd -u $uid --no-log-init -r -g mora mora \
  # Install Poetry. In an isolated environment, following the upstream
  # recommendations https://python-poetry.org/docs/#ci-recommendations
  && python3 -m venv $POETRY_HOME \
  && $POETRY_HOME/bin/pip3 install --no-cache-dir poetry==${POETRY_VERSION}

VOLUME /queries

# Install project dependencies in an isolated environment
ENV VIRTUAL_ENV=/poetry-env \
    PATH="/poetry-env/bin:$POETRY_HOME/bin:$PATH"
WORKDIR /app/backend/
COPY poetry.lock pyproject.toml /app/backend/
RUN python3 -m venv $VIRTUAL_ENV \
    && poetry install --no-interaction \
    && rm -rf /root/.cache
WORKDIR /app/

# Copy and install backend code.
COPY LICENSE .
COPY README.md .
COPY docker ./docker
COPY backend ./backend

# Run the server as the mora user on port 5000
USER mora:mora

# Add build version to the environment last to avoid build cache misses
ARG COMMIT_TAG
ARG COMMIT_SHA
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD} \
    COMMIT_SHA=${COMMIT_SHA}

EXPOSE 5000

CMD ["./docker/start.sh"]
