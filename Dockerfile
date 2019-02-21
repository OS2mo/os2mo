FROM node:carbon as frontend-builder
WORKDIR /code/
COPY frontend ./frontend
WORKDIR /code/frontend
RUN yarn
RUN yarn build


# We do not use alpine. The resulting image is smaller, but there is currently
  # no support for pip installation of wheels (binary) packages. It falls back
  # to installing from source which is very time consuming. See
  # https://github.com/pypa/manylinux/issues/37 and
  # https://github.com/docker-library/docs/issues/904
FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /code/
COPY backend/requirements.txt /code/backend/requirements.txt
COPY backend/requirements-test.txt /code/backend/requirements-test.txt
COPY backend/requirements-docs.txt /code/backend/requirements-docs.txt

RUN set -ex \
  # The -slim version of the debian image deletes man-pages to free space. This
  # unfortunately causes some packages to fail to install. See
  # https://github.com/debuerreotype/debuerreotype/issues/10 As a work-around we
  # add the missing directories for postgresql-client.
  && mkdir -p /usr/share/man/man1 /usr/share/man/man7 \
  && apt-get -y update \
  && apt-get -y install --no-install-recommends \
  # git is needed for python packages with `… = {git = …}` in requirements.txt.
  # It pulls a lot of dependencies. Maybe some of them can be ignored.
  git \
  # psql is used in docker-entrypoint.sh to check for db availability.
  postgresql-client \
  # Python packages dependencies:
  # for xmlsec. TODO: find a binary packages or use a multistage docker
  libxmlsec1-dev \
  gcc \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man/?? /usr/share/man/??_*


RUN pip3 install -r backend/requirements.txt

# Copy application code to the container.
COPY backend ./backend
COPY frontend ./frontend
COPY setup ./setup
RUN pip3 install -e backend

COPY --from=frontend-builder /code/frontend/dist ./frontend/dist

EXPOSE 5000

ENV FLASK_ENV=development
ENV FLASK_APP=mora.app:app

RUN echo '{"LORA_URL": "http://oio_rest:5000/"}' > ./setup/mora.json

# Start gnunicorn
CMD ["python", "-m", "mora.cli", ".", "run", "-h", "0.0.0.0"]
