# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Callable

from prometheus_client import Gauge
from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import default
from prometheus_fastapi_instrumentator.metrics import Info as InstInfo

from .config import get_settings


def setup_metrics(app):
    instrumentator = Instrumentator(should_instrument_requests_inprogress=True)

    # Changes on every request
    instrumentator.add(default())

    # Never changes
    instrumentator.add(os2mo_version())
    instrumentator.add(amqp_enabled())

    instrumentator.instrument(app).expose(app)


def os2mo_version() -> Callable[[InstInfo], None]:
    METRIC = Info("os2mo_version", "Current version")
    settings = get_settings()

    def instrumentation(_: InstInfo) -> None:
        METRIC.info(
            {"mo_version": settings.commit_tag, "mo_commit_sha": settings.commit_sha}
        )

    return instrumentation


def amqp_enabled() -> Callable[[InstInfo], None]:
    """Checks if AMQP is enabled in config.py::Settings"""
    METRIC = Gauge("amqp_enabled", "AMQP enabled")

    def instrumentation(_: InstInfo):
        METRIC.set(get_settings().amqp_enable)

    return instrumentation
