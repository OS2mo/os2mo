# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from pathlib import Path
from itertools import chain

from fastapi import APIRouter, Depends, FastAPI, HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette_context.middleware import RawContextMiddleware
from os2mo_fastapi_utils.auth.oidc import get_auth_exception_handler
from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.tracing import setup_instrumentation, setup_logging
from structlog import get_logger
from structlog.processors import JSONRenderer
from structlog.contextvars import merge_contextvars
from more_itertools import only
from strawberry.asgi import GraphQL

from mora import health, log, config
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.router import keycloak_router
from mora.auth.keycloak.oidc import authorization_exception_handler
from mora.integrations import serviceplatformen
from mora.request_scoped.bulking import request_wide_bulk
from mora.request_scoped.query_args_context_plugin import QueryArgContextPlugin
from mora.graphapi.schema import schema
from tests.util import setup_test_routing
from . import exceptions, lora, service
from . import triggers
from .api.v1 import reading_endpoints
from .config import Environment, get_settings, is_under_test
from .exceptions import ErrorCodes, HTTPException, http_exception_to_json_response
from .metrics import setup_metrics

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, "templates")
distdir = str(Path(basedir).parent.parent / "frontend" / "dist")
logger = get_logger()


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():
        settings = config.get_settings()

        commit_tag = settings.commit_tag
        commit_sha = settings.commit_sha
        mo_version = f"{commit_tag}@{commit_sha}"

        lora_version = await lora.get_version()
        return {
            "mo_version": mo_version,
            "lora_version": lora_version,
        }

    @router.get("/service/{rest_of_path:path}")
    def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router


def static_content_router():
    router = APIRouter()

    @router.get("/")
    @router.get("/organisation/")
    @router.get("/organisation/{path:path}")
    @router.get("/medarbejder/")
    @router.get("/medarbejder/{path:path}")
    @router.get("/organisationssammenkobling/")
    @router.get("/forespoergsler/")
    def index(path=""):
        """Serve index.html on `/` and unknown paths."""
        return FileResponse(distdir + "/index.html")

    @router.get("/favicon.ico")
    def favicon():
        """Serve favicon.ico on `/favicon.ico`."""
        return FileResponse(distdir + "/favicon.ico")

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
    exc = only(filter(
        lambda arg: isinstance(arg, Exception),
        chain(args, kwargs.values())
    ))
    if exc and isinstance(exc, FastAPIHTTPException):
        return http_exception_to_json_response(exc=exc)
    if exc:
        err = ErrorCodes.E_UNKNOWN.to_http_exception(
            message=str(exc)
        )
        return http_exception_to_json_response(exc=err)
    err = ErrorCodes.E_UNKNOWN.to_http_exception(
        message=f"Error details:\nargs: {args}\nkwargs: {kwargs}"
    )
    return http_exception_to_json_response(exc=err)


async def request_validation_handler(
    request: Request, exc: RequestValidationError
):
    """
    Ensure a nicely formatted json response, with

    :param request:
    :param exc:
    :return:
    """
    if not config.is_production():
        logger.info(
            "os2mo_err_details", exc=exc, url=request.url, params=request.query_params
        )

    err = ErrorCodes.E_INVALID_INPUT.to_http_exception(request=exc.body)
    return http_exception_to_json_response(exc=err)


async def http_exception_handler(request: Request, exc: HTTPException):
    if not config.is_production():
        logger.info("http_exception", stack=exc.stack, traceback=exc.traceback)

    return http_exception_to_json_response(exc=exc)


def create_app():
    """
    Create and return a FastApi app instance for MORA.
    """
    log.init()
    middleware = [
        Middleware(
            RawContextMiddleware,
            plugins=(QueryArgContextPlugin(),)
        )
    ]
    tags_metadata = chain([
        {
            "name": "Reading",
            "description": "Data reading endpoints for integrations.",
        },
        {
            "name": "Service",
            "description": "Mixed service data endpoints, supporting the UI.",
        }
    ], [
        {
            "name": "Service." + name,
            "description": "",
        } for name in service.routers.keys()
    ], [
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
            "description": "Endpoints related to testing. Enabled by configuration.",
        },
        {
            "name": "Health",
            "description": "Healthcheck endpoints, called by the observability setup.",
        },
        {
            "name": "Static",
            "description": "Endpoints serving static frontend content.",
        },
    ])
    app = FastAPI(
        middleware=middleware,
        openapi_tags=list(tags_metadata),
    )
    settings = config.get_settings()
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
            router, prefix="/service", tags=["Service." + name],
            dependencies=[Depends(auth)]
        )
    app.include_router(
        reading_endpoints.router, tags=["Reading"],
        dependencies=[Depends(auth)]
    )
    app.include_router(
        keycloak_router(),
        prefix="/service",
        tags=["Auth"],
    )
    app.include_router(
        meta_router(),
        tags=["Meta"],
    )
    app.include_router(
        static_content_router(),
        tags=["Static"],
    )

    if not config.is_production():
        app.include_router(
            setup_test_routing(),
            tags=["Testing"]
        )

    # We serve index.html and favicon.ico here. For the other static files,
    # Flask automatically adds a static view that takes a path relative to the
    # `flaskr/static` directory.
    serviceplatformen.check_config()
    triggers.register(app)

    # TODO: Deal with uncaught "Exception", #43826
    app.add_exception_handler(Exception, fallback_handler)
    app.add_exception_handler(FastAPIHTTPException, fallback_handler)
    app.add_exception_handler(RequestValidationError,
                              request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(
        AuthenticationError,
        get_auth_exception_handler(logger)
    )
    app.add_exception_handler(
        AuthorizationError,
        authorization_exception_handler
    )

    if not is_under_test():
        app = setup_instrumentation(app)
        setup_metrics(app)

    if get_settings().graphql_enable:
        graphql_app = GraphQL(schema)
        app.add_route("/graphql", graphql_app)
        app.add_websocket_route("/subscriptions", graphql_app)

    # Adds pretty printed logs for development
    if get_settings().environment is Environment.DEVELOPMENT:
        setup_logging(processors=[merge_contextvars,
                                  JSONRenderer(indent=2, sort_keys=True)])
    else:
        setup_logging(processors=[merge_contextvars, JSONRenderer()])

    if os.path.exists(distdir):
        app.mount("/", StaticFiles(directory=distdir), name="static")
    else:
        logger.warning('No dist directory to serve', distdir=distdir)

    return app
