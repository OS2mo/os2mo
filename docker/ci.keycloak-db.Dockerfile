# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# This Dockerfile is only used for running the test suite,
# i.e. the unsecure passwords are not important

FROM postgres:13.3

ENV POSTGRES_DB=keycloak
ENV POSTGRES_USER=keycloak
ENV POSTGRES_PASSWORD=keycloak

# The keycloak database runs concurrently with the mox db in CI. On the
# kubernetes gitlab runner, all services run in the same pod, which means that
# we cannot reuse the same port for multiple services.
ENV POSTGRES_PORT=2345
EXPOSE 2345
