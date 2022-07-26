# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0


from fastapi import FastAPI
from oio_rest.metrics import setup_metrics
from os2mo_fastapi_utils.tracing import setup_instrumentation, setup_logging
from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.oidc import get_auth_exception_handler
from structlog import get_logger
from structlog.contextvars import merge_contextvars
from structlog.processors import JSONRenderer
from oio_rest.views import setup_views

logger = get_logger()


def create_app():
    app = FastAPI()
    app = setup_instrumentation(app)
    app.add_exception_handler(AuthenticationError, get_auth_exception_handler(logger))

    setup_metrics(app)
    setup_views(app)
    setup_logging(processors=[merge_contextvars, JSONRenderer()])

    return app
