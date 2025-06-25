# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import sys
from contextlib import asynccontextmanager
from itertools import chain
from typing import Any

import sentry_sdk
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastramqpi.ramqp import AMQPSystem
from more_itertools import only
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.custom_exceptions import OIOException
from oio_rest.views import create_lora_router
from prometheus_client import Gauge
from prometheus_client import Info
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.strawberry import StrawberryIntegration
from sqlalchemy.exc import DataError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import RawContextMiddleware
from structlog import get_logger

from mora import config
from mora import health
from mora import log
from mora.auth.exceptions import AuthenticationError
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import authorization_exception_handler
from mora.auth.keycloak.oidc import service_api_auth
from mora.auth.keycloak.router import keycloak_router
from mora.auth.middleware import set_authenticated_user
from mora.common import lora_connector_context
from mora.db.events import setup_event_metrics
from mora.graphapi.middleware import is_graphql_context
from mora.request_scoped.query_args_context_plugin import query_args_context
from mora.service.address_handler.dar import dar_loader_context
from mora.service.shimmed.meta import meta_router
from mora.util import now_per_request

from . import service
from . import testing
from . import triggers
from .auth.exceptions import get_auth_exception_handler
from .config import Environment
from .db import create_sessionmaker
from .db import transaction_per_request
from .exceptions import ErrorCodes
from .exceptions import HTTPException
from .exceptions import http_exception_to_json_response
from .graphapi.router import router as graphapi_router
from .graphapi.shim import set_graphql_context_dependencies
from .lora import lora_noop_change_context

logger = get_logger()

# PYTHONDEVMODE: https://docs.python.org/3/library/devmode.html
if sys.flags.dev_mode:
    logger.warning(
        "Python Development Mode is enabled. Performance may be significantly impacted!"
    )


METRIC_MO_INFO = Info("os2mo_version", "Current version")
METRIC_AMQP_ENABLED = Gauge("amqp_enabled", "AMQP enabled")


async def fallback_handler(*args, **kwargs) -> JSONResponse:
    """
    Ensure a nicely formatted json response, with
    minimal knowledge about the exception available.

    When used to handle ANY error, special care needs to be taken. This is a custom
    solution to a known problem:
    https://stackoverflow.com/questions/61596911/catch-exception-in-fast-api-globally#comment113231014_61608398
    https://github.com/tiangolo/fastapi/issues/2750#issuecomment-775526951
    :return:
    """
    exc = only(
        filter(lambda arg: isinstance(arg, Exception), chain(args, kwargs.values()))
    )
    if exc and isinstance(exc, FastAPIHTTPException):
        return http_exception_to_json_response(exc=exc)
    if exc:
        err = ErrorCodes.E_UNKNOWN.to_http_exception(message=str(exc))
        return http_exception_to_json_response(exc=err)
    # coverage: pause
    err = ErrorCodes.E_UNKNOWN.to_http_exception(
        message=f"Error details:\nargs: {args}\nkwargs: {kwargs}"
    )
    return http_exception_to_json_response(exc=err)
    # coverage: unpause


async def request_validation_handler(request: Request, exc: RequestValidationError):
    """
    Ensure a nicely formatted json response, with

    :param request:
    :param exc:
    :return:
    """
    settings = config.get_settings()
    if not settings.is_production():  # pragma: no cover
        logger.info(
            "os2mo_err_details", exc=exc, url=request.url, params=request.query_params
        )

    err = ErrorCodes.E_INVALID_INPUT.to_http_exception(
        request=exc.body, errors=exc.errors()
    )
    return http_exception_to_json_response(exc=err)


async def http_exception_handler(request: Request, exc: HTTPException):
    settings = config.get_settings()
    if not settings.is_production():
        logger.info("http_exception", stack=exc.stack, traceback=exc.traceback)

    return http_exception_to_json_response(exc=exc)


def create_app(settings_overrides: dict[str, Any] | None = None):
    """
    Create and return a FastApi app instance for MORA.
    """
    settings_overrides = settings_overrides or {}
    settings = config.get_settings(**settings_overrides)

    log.init(
        log_level=settings.log_level,
        json=settings.environment is not Environment.DEVELOPMENT,
    )
    tags_metadata = chain(
        [
            {
                "name": "Reading",
                "description": "Data reading endpoints for integrations.",
            },
            {
                "name": "Service",
                "description": "Mixed service data endpoints, supporting the UI.",
            },
        ],
        [
            {
                "name": "Service." + name,
                "description": "",
            }
            for name in service.routers.keys()
        ],
        [
            {
                "name": "Auth",
                "description": "Authentication endpoints.",
            },
            {
                "name": "Meta",
                "description": "Various unrelated endpoints.",
            },
            {
                "name": "Testing",
                "description": "Endpoints related to testing. "
                "Enabled by configuration.",
            },
            {
                "name": "Health",
                "description": "Healthcheck endpoints. "
                "Called by the observability setup.",
            },
        ],
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        instrumentator.expose(app)

        await triggers.register(app)
        if settings.amqp_enable:
            async with app.state.amqp_system:
                yield
        else:
            yield

    lora_settings = lora_get_settings()
    sessionmaker = create_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=lora_settings.db_name,
    )

    app = FastAPI(
        lifespan=lifespan,
        middleware=[
            Middleware(RawContextMiddleware),
            Middleware(BaseHTTPMiddleware, dispatch=lora_noop_change_context),
            Middleware(BaseHTTPMiddleware, dispatch=log.gen_accesslog_middleware()),
            Middleware(
                # CORS headers describe which origins are permitted to contact the server, and
                # specify which authentication credentials (e.g. cookies or headers) should be
                # sent. CORS is NOT a server-side security mechanism, but relies on the browser
                # itself to enforce it.
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
                # https://www.starlette.io/middleware/#corsmiddleware
                CORSMiddleware,
                # Allow any website to contact the API. The MO frontend is not special in any
                # way, and we want to allow the customer to use the API from their own sites
                # without any additional configuration in the backend - it should be agnostic.
                # Note that setting this to wildcard blocks Set-Cookie headers by the browser.
                allow_origins=["*"],
                # Allow the HTTP methods needed by the REST and GraphQL APIs.
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
                allow_methods=[
                    "GET",
                    "HEAD",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "OPTIONS",
                ],
                # Allow JavaScript to set the following HTTP headers. The headers `Accept`,
                # `Accept-Language`, `Content-Language`, and `Content-Type` are always allowed.
                allow_headers=["Authorization"],
                # Allow JavaScript to access the following HTTP headers from requests.
                expose_headers=["Link", "Location"],
                # Don't allow the browser to send cookies with the request. Allowing
                # credentials is incompatible with the settings above, as the browser blocks
                # credentialed requests if the server allows wildcard origin, methods, or
                # headers. Even so, we would not want to allow cookies anyway, as they offer
                # dangerous automatic, implicit authentication. This allows any website to make
                # requests to the API on behalf of an already-logged in user. The API requires
                # the explicit usage of JWTs through the Authorization header instead, which
                # requires the requesting JavaScript to obtain access tokens directly.
                allow_credentials=False,
            ),
        ],
        dependencies=[
            Depends(now_per_request),
            Depends(log.canonical_log_dependency),
            Depends(transaction_per_request),
            Depends(set_authenticated_user),
            Depends(query_args_context),
            Depends(lora_connector_context),
            Depends(dar_loader_context),
            Depends(is_graphql_context),
            Depends(set_graphql_context_dependencies),
        ],
        openapi_tags=list(tags_metadata),
    )

    instrumentator = Instrumentator().instrument(app)
    METRIC_MO_INFO.info(
        {
            "mo_version": settings.commit_tag or "unversioned",
            "mo_commit_sha": settings.commit_sha or "no sha",
        }
    )
    METRIC_AMQP_ENABLED.set(settings.amqp_enable)
    setup_event_metrics(instrumentator)

    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"],
    )

    for name, router in service.routers.items():
        app.include_router(
            router,
            prefix="/service",
            tags=["Service." + name],
            dependencies=[Depends(auth), Depends(service_api_auth)],
        )
    for name, router in service.no_auth_routers.items():
        app.include_router(
            router,
            prefix="/service",
            tags=["Service." + name],
        )

    app.include_router(
        graphapi_router,
        tags=["GraphQL"],
    )

    if settings.os2mo_auth:
        app.include_router(
            keycloak_router(),
            prefix="/service",
            tags=["Auth"],
        )
    app.include_router(
        meta_router(),
        tags=["Meta"],
    )

    if settings.insecure_enable_testing_api:
        app.include_router(
            testing.router,
            prefix="/testing",
            tags=["Testing"],
        )

    if settings.expose_lora:
        app.include_router(create_lora_router(), prefix="/lora")

    # Set up lifecycle state for depends.py
    app.state.sessionmaker = sessionmaker
    amqp_system = AMQPSystem(settings.amqp)
    app.state.amqp_system = amqp_system

    # TODO: Deal with uncaught "Exception", #43826
    app.add_exception_handler(Exception, fallback_handler)
    app.add_exception_handler(FastAPIHTTPException, fallback_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(AuthenticationError, get_auth_exception_handler(logger))
    app.add_exception_handler(AuthorizationError, authorization_exception_handler)

    # These two exception handlers are for LoRas API:
    @app.exception_handler(OIOException)
    def handle_not_allowed(request: Request, exc: OIOException):
        dct = exc.to_dict()
        return JSONResponse(status_code=exc.status_code, content=dct)

    @app.exception_handler(DataError)
    def handle_db_error(request: Request, exc: DataError):
        message = exc.orig.diag.message_primary
        context = exc.orig.diag.context
        return JSONResponse(
            status_code=400, content={"message": message, "context": context}
        )

    if settings.sentry_dsn:  # pragma: no cover
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                StrawberryIntegration(async_execution=True),
            ],
        )

    return app
