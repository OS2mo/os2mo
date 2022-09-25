# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from itertools import chain
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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
from mora.graphapi.middleware import IdempotencyTokenPlugin
from mora.request_scoped.bulking import request_wide_bulk
from mora.request_scoped.query_args_context_plugin import QueryArgContextPlugin
from mora.service.address_handler.dar import DARLoaderPlugin
from mora.service.shimmed.meta import meta_router
from oio_rest.app import create_app as create_lora_app
from tests.util import setup_test_routing

basedir = os.path.dirname(__file__)
distdir = str(Path(basedir).parent.parent / "frontend" / "dist")
logger = get_logger()


def static_content_router():
    router = APIRouter()

    @router.get("/favicon.ico", response_class=FileResponse)
    def favicon():
        """Serve favicon.ico on `/favicon.ico`."""
        return FileResponse(
            distdir + "/favicon.ico", media_type="image/vnd.microsoft.icon"
        )

    @router.get("/", response_class=HTMLResponse)
    @router.get("/{path:path}", response_class=HTMLResponse)
    def index(path=""):
        """Serve index.html on `/` and unknown paths."""
        return FileResponse(distdir + "/index.html")

    return router


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
                IdempotencyTokenPlugin(),
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
            {
                "name": "Static",
                "description": "Endpoints serving static frontend content.",
            },
        ],
    )
    app = FastAPI(
        middleware=middleware,
        openapi_tags=list(tags_metadata),
    )
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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

    if settings.graphql_enable:
        setup_graphql(app=app, enable_graphiql=settings.graphiql_enable)

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

    if not settings.is_production() and settings.testcafe_enable:
        app.include_router(setup_test_routing(), tags=["Testing"])

    # Mount all of Lora in
    if settings.enable_internal_lora:
        lora_app = create_lora_app()
        app.mount("/lora", lora_app)

    # Statics must be included last because of the wildcard, matching anything unhandled
    if settings.statics_enable:
        if os.path.exists(distdir):
            app.mount(
                "/static/", StaticFiles(directory=distdir + "/static/"), name="static"
            )
        else:
            logger.warning("No dist directory to serve", distdir=distdir)
        app.include_router(
            static_content_router(),
            tags=["Static"],
        )

    # TODO: Deal with uncaught "Exception", #43826
    app.add_exception_handler(Exception, fallback_handler)
    app.add_exception_handler(FastAPIHTTPException, fallback_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(AuthenticationError, get_auth_exception_handler(logger))
    app.add_exception_handler(AuthorizationError, authorization_exception_handler)

    @app.on_event("startup")
    async def startup():
        await triggers.register(app)
        if lora.client is not None:
            return
        if settings.enable_internal_lora:
            lora.client = await lora.create_lora_client(app)
        else:
            lora.client = await lora.create_lora_client()

    @app.on_event("shutdown")
    async def shutdown():
        await triggers.internal.amqp_trigger.stop_amqp()
        # Leaking intentional so the test suite will re-use the lora.client.
        # await lora.client.aclose()

    if not settings.is_under_test():
        setup_metrics(app)

    app.add_middleware(log.AccesslogMiddleware)

    return app
