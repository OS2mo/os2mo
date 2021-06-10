# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
import os
from copy import deepcopy
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette_context.middleware import RawContextMiddleware

from mora import __version__, health, log
from mora.auth.exceptions import AuthError
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import auth_exception_handler
from mora.auth.keycloak.oidc import add_keycloak
from mora.integrations import serviceplatformen
from mora.request_scoped.bulking import request_wide_bulk
from mora.request_scoped.query_args import current_query
from tests.util import setup_test_routing
from . import exceptions, lora, service
from . import triggers
from .api.v1 import reading_endpoints
from .exceptions import ErrorCodes, HTTPException, http_exception_to_json_response
from .settings import config

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, "templates")
distdir = str(Path(basedir).parent.parent / "frontend" / "dist")
logger = logging.getLogger(__name__)


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():
        lora_version = await lora.get_version()
        return {
            "mo_version": __version__,
            "lora_version": lora_version,
        }

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

    @router.get("/service/{rest_of_path:path}")
    def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

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
    # look for exception
    if len(args) in [2, 3] and isinstance(args[-1], Exception):
        exc = args[-1]
    elif 'exc' in kwargs and isinstance(kwargs['exc'], Exception):
        exc = kwargs['exc']
    else:  # desperate fallback
        err = ErrorCodes.E_UNKNOWN.to_http_exception(
            message=f"Error details:\nargs: {args}\nkwargs: {kwargs}"
        )
        return http_exception_to_json_response(exc=err)

    # properly, backwards compatible exception-handling
    err = ErrorCodes.E_UNKNOWN.to_http_exception(message=str(exc))
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
    if config["ENV"] in ["development", "testing"]:
        logger.info(
            f"os2mo err details\n{exc}\n"
            f"request url:\n{request.url}\n"
            f"request params:\n{request.query_params}"
        )

    err = ErrorCodes.E_INVALID_INPUT.to_http_exception(request=exc.body)
    return http_exception_to_json_response(exc=err)


async def http_exception_handler(request: Request, exc: HTTPException):
    if config["ENV"] in ["development", "testing"]:
        if exc.stack is not None:
            for frame in exc.stack:
                logger.info(frame)
        if exc.traceback is not None:
            logger.info(f"os2mo traceback\n{exc.traceback}")

    return http_exception_to_json_response(exc=exc)


def create_app():
    """
    Create and return a FastApi app instance for MORA.
    """
    log.init()
    middleware = [Middleware(RawContextMiddleware)]
    app = FastAPI(
        middleware=middleware,
    )
    app = add_keycloak(app)

    if config["enable_cors"]:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def manage_request_scoped_globals(request: Request, call_next):
        with current_query.context_args(deepcopy(request.query_params)):
            async with request_wide_bulk.cache_context():
                # #HACK: needed to access the body of the request in the middleware
                # #https://github.com/encode/starlette/issues/495#issuecomment-513138055

                # async def set_body(request: Request, body: bytes):
                #     async def receive() -> Message:
                #         return {"type": "http.request", "body": body}
                #
                #     request._receive = receive
                #
                # async def get_body(request: Request) -> bytes:
                #     body = await request.body()
                #     await set_body(request, body)
                #     return body
                response = await call_next(request)
        return response

    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"],
    )

    for router in service.routers:
        app.include_router(
            router, prefix="/service", tags=["Service"],
            dependencies=[Depends(auth)]
        )
    app.include_router(
        reading_endpoints.router,
        dependencies=[Depends(auth)]
    )
    app.include_router(
        meta_router(),
        tags=["Meta"],
    )

    if config['ENV'] in ['testing', 'development']:
        app = setup_test_routing(app)

    # We serve index.html and favicon.ico here. For the other static files,
    # Flask automatically adds a static view that takes a path relative to the
    # `flaskr/static` directory.
    serviceplatformen.check_config()
    triggers.register(app)
    if os.path.exists(distdir):
        app.mount("/", StaticFiles(directory=distdir), name="static")
    else:
        logger.warning(f'No dist directory to serve! (Missing: {distdir})')

    return app
