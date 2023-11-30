# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
from operator import attrgetter
from uuid import UUID

from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from jinja2 import Environment
from jinja2 import FileSystemLoader
from psycopg2 import DataError
from structlog import get_logger

from oio_rest import klassifikation
from oio_rest import organisation
from oio_rest.custom_exceptions import OIOException
from oio_rest.mo.autocomplete import find_org_units_matching
from oio_rest.mo.autocomplete import find_users_matching

logger = get_logger()

current_directory = os.path.dirname(os.path.realpath(__file__))

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(current_directory, "templates", "html"))
)


def setup_views(app):
    @app.get("/", tags=["Meta"])
    async def root():
        return RedirectResponse(app.url_path_for("sitemap"))

    @app.get("/site-map", tags=["Meta"])
    async def sitemap():
        """Returns a site map over all valid urls.

        .. :quickref: :http:get:`/site-map`

        """
        links = app.routes
        links = filter(lambda route: "GET" in route.methods, links)
        links = map(attrgetter("path"), links)
        return {"site-map": sorted(links)}

    @app.get("/autocomplete/bruger")
    def autocomplete_user(
        phrase: str,
        class_uuids: list[UUID] | None = Query(None),
    ):
        return {"results": find_users_matching(phrase, class_uuids=class_uuids)}

    @app.get("/autocomplete/organisationsenhed")
    def autocomplete_org_unit(
        phrase: str, class_uuids: list[UUID] | None = Query(None)
    ):
        return {"results": find_org_units_matching(phrase, class_uuids=class_uuids)}

    app.include_router(
        klassifikation.KlassifikationsHierarki.setup_api(),
        tags=["Klassifikation"],
    )

    app.include_router(
        organisation.OrganisationsHierarki.setup_api(),
        tags=["Organisation"],
    )

    @app.exception_handler(OIOException)
    def handle_not_allowed(request: Request, exc: OIOException):
        dct = exc.to_dict()
        return JSONResponse(status_code=exc.status_code, content=dct)

    @app.exception_handler(HTTPException)
    def http_exception(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.status_code, "text": str(exc.detail)},
        )

    @app.exception_handler(DataError)
    def handle_db_error(request: Request, exc: DataError):
        message = exc.diag.message_primary
        context = exc.diag.context or exc.pgerror.split("\n", 1)[-1]
        return JSONResponse(
            status_code=400, content={"message": message, "context": context}
        )

    @app.exception_handler(ValueError)
    def handle_value_error(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"message": str(exc)})
