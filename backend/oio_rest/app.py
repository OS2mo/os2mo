# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import Depends
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware

from mora.auth.middleware import set_authenticated_user
from oio_rest.views import setup_views


def create_app():
    app = FastAPI(
        middleware=[Middleware(RawContextMiddleware)],
        dependencies=[
            # This middleware is also found in OS2mo itself.
            # This is an attempt to ensure that the context variable is always set.
            # Even when crossing the HTTPX boundary from lora.py into LoRa.
            Depends(set_authenticated_user),
        ],
    )
    setup_views(app)
    return app
