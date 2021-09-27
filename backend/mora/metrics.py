# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Callable

from mora.health import dar, dataset, oio_rest, amqp
from prometheus_client import Info, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info as InstInfo, default

from .config import get_settings


def setup_metrics(app):
    instrumentator = Instrumentator(should_instrument_requests_inprogress=True)

    instrumentator.add(default())
    instrumentator.add(os2mo_version())
    instrumentator.add(amqp_enabled())
    if get_settings().amqp_enable:
        instrumentator.add(amqp_health())
    instrumentator.add(oio_rest_health())
    instrumentator.add(dataset_health())
    instrumentator.add(dar_health())

    instrumentator.instrument(app).expose(app)


def os2mo_version() -> Callable[[InstInfo], None]:
    METRIC = Info('os2mo_version', 'Current version')
    settings = get_settings()

    def instrumentation(_: InstInfo) -> None:
        METRIC.info({
            "mo_version": settings.commit_tag,
            "mo_commit_sha": settings.commit_sha
        })
    return instrumentation


def amqp_enabled() -> Callable[[InstInfo], None]:
    """Checks if AMQP is enabled in config.py::Settings
    """
    METRIC = Gauge('amqp_enabled', 'AMQP enabled')

    def instrumentation(_: InstInfo):
        METRIC.set(get_settings().amqp_enable)

    return instrumentation


def amqp_health() -> Callable[[InstInfo], None]:
    """Check if AMQP connection is open.

    Updates metric with `True` if open. `False` if not open or an error occurs.
    Doesn't run if AMQP support is disabled.
    """
    METRIC = Gauge('amqp_health', 'AMQP health')

    def instrumentation(_: InstInfo) -> None:
        METRIC.set(amqp())

    return instrumentation


def oio_rest_health() -> Callable[[InstInfo], None]:
    """Check if the configured oio_rest can be reached
    True if reachable. False if not
    """
    METRIC = Gauge('oio_rest_health', 'OIO REST health')

    def instrumentation(_: InstInfo) -> None:
        METRIC.set(oio_rest())

    return instrumentation


def dataset_health() -> Callable[[InstInfo], None]:
    """Check if LoRa contains data. We check this by determining if an organisation
    exists in the system
    True if data. False if not.
    """
    METRIC = Gauge('dataset_health', 'Dataset health')

    async def instrumentation(_: InstInfo):
        METRIC.set(await dataset())

    return instrumentation


def dar_health() -> Callable[[InstInfo], None]:
    """Check whether DAR can be reached
    True if reachable. False if not.
    """
    METRIC = Gauge('dar_health', 'DAR health')

    def instrumentation(_: InstInfo):
        METRIC.set(dar())

    return instrumentation
