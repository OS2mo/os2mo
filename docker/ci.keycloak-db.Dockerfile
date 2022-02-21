# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

# This Dockerfile is only used for running the test suite,
# i.e. the unsecure passwords are not important

FROM postgres:13.3

ENV POSTGRES_DB=keycloak
ENV POSTGRES_USER=keycloak
ENV POSTGRES_PASSWORD=keycloak
