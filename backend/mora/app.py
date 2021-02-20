# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os
import typing

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

import mora.async_util
from mora import __version__, log
from mora import health
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

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, 'templates')
distdir = os.path.join(basedir, '..', '..', 'frontend', 'dist')


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
    @router.get("/organisation/<path:path>")
    @router.get("/medarbejder/")
    @router.get("/medarbejder/<path:path>")
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

    @router.get("/service/<path:path>")
    def no_such_endpoint(path=""):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router


def create_app(overrides: typing.Dict[str, typing.Any] = None):
    '''Create and return a Flask app instance for MORA.

    :param dict overrides: Settings to override prior to extension
                           instantiation.

    '''

    log.init()

    app = FastAPI()

    # app.config.update(settings.app_config)
    # app.url_map.converters['uuid'] = util.StrUUIDConverter

    #if overrides is not None:
    #    app.config.update(overrides)

    app.include_router(base.router, prefix="/service", tags=["Service"])

    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"],
    )

    app.include_router(
        meta_router(),
        tags=["Meta"],
    )

    for router in service.routers:
        app.include_router(router, prefix="/service", tags=["Service"])

#    @app.errorhandler(Exception)
#    def handle_invalid_usage(error):
#        """
#        Handles errors in case an exception is raised.
#
#        :param error: The error raised.
#        :return: JSON describing the problem and the apropriate status code.
#        """
#
#        if not isinstance(error, werkzeug.routing.RoutingException):
#            util.log_exception('unhandled exception')
#
#        if not isinstance(error, werkzeug.exceptions.HTTPException):
#            error = exceptions.HTTPException(
#                description=str(error),
#            )
#
#        return error.get_response(flask.request.environ)
    # We serve index.html and favicon.ico here. For the other static files,
    # Flask automatically adds a static view that takes a path relative to the
    # `flaskr/static` directory.

    # serviceplatformen.check_config(app)
    # triggers.register(app)

    app.mount("/", StaticFiles(directory=distdir), name="static")

    return app
