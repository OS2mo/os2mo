# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
from itertools import chain
from pathlib import Path
from typing import Any

import sentry_sdk
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from more_itertools import only
from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.oidc import get_auth_exception_handler
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette_context.middleware import RawContextMiddleware
from structlog import get_logger

from . import lora
from . import service
from . import triggers
from .common import LoRaConnectorPlugin
from .config import Environment
from .exceptions import ErrorCodes
from .exceptions import http_exception_to_json_response
from .exceptions import HTTPException
from .metrics import setup_metrics
from mora import config
from mora import health
from mora import log
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import authorization_exception_handler
from mora.auth.keycloak.router import keycloak_router
from mora.graphapi.main import setup_graphql
from mora.graphapi.middleware import GraphQLContextPlugin
from mora.graphapi.middleware import GraphQLDatesPlugin
from mora.request_scoped.bulking import request_wide_bulk
from mora.request_scoped.query_args_context_plugin import QueryArgContextPlugin
from mora.service.address_handler.dar import DARLoaderPlugin
from mora.service.shimmed.meta import meta_router
from oio_rest.app import create_app as create_lora_app


basedir = os.path.dirname(__file__)
distdir = str(Path(basedir).parent.parent / "frontend" / "dist")
logger = get_logger()


async def fallback_handler(*args, **kwargs):
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
    err = ErrorCodes.E_UNKNOWN.to_http_exception(
        message=f"Error details:\nargs: {args}\nkwargs: {kwargs}"
    )
    return http_exception_to_json_response(exc=err)


async def request_validation_handler(request: Request, exc: RequestValidationError):
    """
    Ensure a nicely formatted json response, with

    :param request:
    :param exc:
    :return:
    """
    settings = config.get_settings()
    if not settings.is_production():
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
        log_level=settings.os2mo_log_level,
        json=settings.environment is not Environment.DEVELOPMENT,
    )
    middleware = [
        Middleware(
            RawContextMiddleware,
            plugins=(
                QueryArgContextPlugin(),
                LoRaConnectorPlugin(),
                DARLoaderPlugin(),
                GraphQLContextPlugin(),
                GraphQLDatesPlugin(),
            ),
        )
    ]
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
    app = FastAPI(
        middleware=middleware,
        openapi_tags=list(tags_metadata),
    )

    # CORS headers describe which origins are permitted to contact the server, and
    # specify which authentication credentials (e.g. cookies or headers) should be
    # sent. CORS is NOT a server-side security mechanism, but relies on the browser
    # itself to enforce it.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    # https://www.starlette.io/middleware/#corsmiddleware
    app.add_middleware(
        CORSMiddleware,
        # Allow any website to contact the API. The MO frontend is not special in any
        # way, and we want to allow the customer to use the API from their own sites
        # without any additional configuration in the backend - it should be agnostic.
        # Note that setting this to wildcard blocks Set-Cookie headers by the browser.
        allow_origins=["*"],
        # Allow the HTTP methods needed by the REST and GraphQL APIs.
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
        allow_methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
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
    )

    @app.middleware("http")
    async def manage_request_scoped_globals(request: Request, call_next):
        async with request_wide_bulk.cache_context():
            return await call_next(request)

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
            dependencies=[Depends(auth)],
        )
    for name, router in service.no_auth_routers.items():
        app.include_router(
            router,
            prefix="/service",
            tags=["Service." + name],
        )

    setup_graphql(app=app)

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

    # Mount all of Lora in
    lora_app = create_lora_app()
    app.mount("/lora", lora_app)

    # TODO: Deal with uncaught "Exception", #43826
    app.add_exception_handler(Exception, fallback_handler)
    app.add_exception_handler(FastAPIHTTPException, fallback_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(AuthenticationError, get_auth_exception_handler(logger))
    app.add_exception_handler(AuthorizationError, authorization_exception_handler)

    @app.on_event("startup")
    async def startup():
        if not settings.is_under_test():
            setup_metrics(app)

        await triggers.register(app)
        if lora.client is not None:
            return
        lora.client = await lora.create_lora_client(app)

    @app.on_event("shutdown")
    async def shutdown():
        await triggers.internal.amqp_trigger.stop_amqp()
        # Leaking intentional so the test suite will re-use the lora.client.
        # await lora.client.aclose()

    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn)

    app.add_middleware(log.AccesslogMiddleware)

    return app
