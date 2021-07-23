# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Callable
from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info as InstInfo

from . import __version__
from .config import Environment, get_settings


def setup_metrics(app):
    if get_settings().environment is Environment.TESTING:
        return

    instrumentator = Instrumentator()
    instrumentator.add(os2mo_version())
    instrumentator.instrument(app).expose(app)


def os2mo_version() -> Callable[[InstInfo], None]:
    METRIC = Info('os2mo_version', 'Current versions')

    def instrumentation(_: InstInfo) -> None:
        METRIC.info({"mo_version": __version__})

    return instrumentation
