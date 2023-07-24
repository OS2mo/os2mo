# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware

from oio_rest.views import setup_views


def create_app():
    app = FastAPI(middleware=[Middleware(RawContextMiddleware)])
    setup_views(app)
    return app
