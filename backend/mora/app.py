# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
import os
from copy import deepcopy
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette_context.middleware import RawContextMiddleware

from mora import __version__, health, log, triggers
from mora.auth import base
from . import exceptions
from . import lora
from . import service
from . import settings
from . import util
from .api.v1 import read_orgfunk
from .auth import base
from .integrations import serviceplatformen
from . import triggers
from mora.auth import base
from .exceptions import ErrorCodes, http_exception_to_json_response
import request_scoped_globals
from mora.integrations import serviceplatformen
from mora.request_scoped.bulking import request_wide_bulk
from mora.request_scoped.query_args import current_query
from tests.util import setup_test_routing
from . import exceptions, lora, service
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
    @router.get("/hjaelp/")
    @router.get("/organisationssammenkobling/")
    @router.get("/forespoergsler/")
    @router.get("/tidsmaskine/")
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


async def fallback_handler(request, exc):
    """
    Ensure a nicely formatted json response, with
    minimal knowledge about the exception available.
    :param request:
    :param exc:
    :return:
    """
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
        logger.debug(
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
                logger.debug(frame)
        if exc.traceback is not None:
            logger.debug(f"os2mo traceback\n{exc.traceback}")

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

    # router include order matters
    app.include_router(base.router, prefix="/service", tags=["Service"])

    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"],
    )

    for router in service.routers:
        app.include_router(router, prefix="/service", tags=["Service"])
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

    app.add_exception_handler(Exception, fallback_handler)
    app.add_exception_handler(FastAPIHTTPException, fallback_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    return app
