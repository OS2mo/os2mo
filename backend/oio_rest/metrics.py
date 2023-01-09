# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import default
from prometheus_fastapi_instrumentator.metrics import Info as InstInfo

from oio_rest.config import get_settings


def setup_metrics(app):
    instrumentator = Instrumentator(should_instrument_requests_inprogress=True)

    instrumentator.add(default())
    instrumentator.add(lora_version())

    instrumentator.instrument(app).expose(app)


def lora_version() -> Callable[[InstInfo], None]:
    METRIC = Info("lora_version", "Current version")

    settings = get_settings()

    def instrumentation(_: InstInfo) -> None:
        METRIC.info(
            {
                "lora_version": settings.commit_tag,
                "lora_commit_sha": settings.commit_sha,
            }
        )

    return instrumentation
