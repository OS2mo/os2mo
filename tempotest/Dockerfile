# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
FROM golang:1.17 as build

WORKDIR /go/src/app

RUN go install -trimpath go.k6.io/xk6/cmd/xk6@latest && \
    xk6 build --with github.com/grafana/xk6-output-prometheus-remote@latest


# TODO: Remove ':debug' (shell etc.) when https://gitlab.com/gitlab-org/gitlab-runner/-/issues/26501 is fixed (never).
FROM gcr.io/distroless/static-debian11:debug
COPY --from=build /go/src/app /
COPY *.js /
COPY tests/ /tests/

ENTRYPOINT ["/k6", "run", "script.js"]
