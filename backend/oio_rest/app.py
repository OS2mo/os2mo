# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import FastAPI

from oio_rest.views import setup_views


def create_app():
    app = FastAPI()
    setup_views(app)
    return app
