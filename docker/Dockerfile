# We use a multistage build to build the Vue.js frontend in a seperate stage.
FROM node:10 AS frontend-builder

WORKDIR /code/frontend

COPY frontend/package.json .
COPY frontend/yarn.lock .
# We fail hard if the yaml.lock is outdated.
RUN yarn install --frozen-lockfile

COPY frontend .
RUN yarn build


# We do not use alpine. The resulting image is smaller, but there is currently
# no support for pip installation of wheels (binary) packages. It falls back to
# installing from source which is very time consuming. See
# https://github.com/pypa/manylinux/issues/37 and
# https://github.com/docker-library/docs/issues/904
#
# We also don't use -slim as some python packages are not wheels and needs
# compiling with the tools for the non -slim image.
FROM python:3.6 AS dist


LABEL org.opencontainers.image.title="OS2mo - Medarbejder og Organisation" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2.eu/produkt/os2mo" \
      org.opencontainers.image.documentation="https://os2mo.readthedocs.io" \
      org.opencontainers.image.source="https://github.com/OS2mo/os2mo"


# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=mora.app:create_app


WORKDIR /code/
COPY docker/sys-requirements.txt sys-requirements.txt
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
  # Install system dependencies from file.
  && apt-get -y update \
  && apt-get -y install --no-install-recommends $(grep -vE "^\s*#" sys-requirements.txt  | tr "\n" " ") \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man/?? /usr/share/man/??_*


# Install requirements
COPY backend/requirements.txt /code/backend/requirements.txt
COPY backend/requirements-test.txt /code/backend/requirements-test.txt
COPY backend/requirements-docs.txt /code/backend/requirements-docs.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r backend/requirements.txt -r backend/requirements-test.txt


# Copy and install backend code.
COPY docker ./docker
COPY backend ./backend
COPY README.rst .
COPY NEWS.rst .
COPY LICENSE .
# Install the application as editable. This makes it possible to mount
# `/code/backend` to your host and edit the files during development.
RUN pip3 install -e backend


# Copy frontend code.
COPY --from=frontend-builder /code/frontend/package.json ./frontend/package.json
COPY --from=frontend-builder /code/frontend/dist ./frontend/dist

RUN install -g mora -o mora -d /var/log/mox
RUN install -g mora -o mora /dev/null /var/log/mox/activity.log

# Run the server as the mora user on port 5000
USER mora:mora
EXPOSE 5000
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "mora.app:create_app()"]
