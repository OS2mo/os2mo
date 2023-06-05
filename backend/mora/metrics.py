# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from prometheus_client import Gauge
from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator

from .config import get_settings


def setup_metrics(app):
    Instrumentator().instrument(app).expose(app)

    settings = get_settings()
    Info("os2mo_version", "Current version").info(
        {
            "mo_version": settings.commit_tag or "unversioned",
            "mo_commit_sha": settings.commit_sha or "no sha",
        }
    )
    Gauge("amqp_enabled", "AMQP enabled").set(get_settings().amqp_enable)
