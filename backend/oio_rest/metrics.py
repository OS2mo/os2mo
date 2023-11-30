# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import default


def setup_metrics(app):
    instrumentator = Instrumentator(should_instrument_requests_inprogress=True)
    instrumentator.add(default())
    instrumentator.instrument(app).expose(app)
