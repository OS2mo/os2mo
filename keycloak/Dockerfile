# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

FROM quay.io/keycloak/keycloak:23.0.4-0

# Mitigation for CVE-2026-114938 (Java4Shell). Only remove this line if the
# image above is updated to at least 26.8.2.
# https://www.keycloak.org/2026/11/java4shell-vulnerability-cve-2026-114938
ENV JAVA_OPTS_APPEND=-XX:-UseBASE64Intrinsics

# It is recommended to "build" Keycloak with a configuration for faster
# startup. The build-time options can no longer be changed by environment
# variables as the code-paths have been eliminated. Build options have a little
# 🔧 next to them in the manual:
# https://www.keycloak.org/server/all-config
COPY ./keycloak.conf /opt/keycloak/conf/

RUN /opt/keycloak/bin/kc.sh build

CMD ["start", "-Dkeycloak.saml.deprecated.encryption=true"]
