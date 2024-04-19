# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import importlib
import re
import time

from fastapi import APIRouter
from fastapi import FastAPI
from more_itertools import first
from more_itertools import last
from starlette import status
from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.requests import Request
import structlog
from fastapi import HTTPException


logger = structlog.get_logger()

graphql_versions = list(range(2, 22))


def setup_graphql(
    app: FastAPI, min_version: int | None = None
) -> None:
    versions = graphql_versions

    if min_version is not None:
        versions = [x for x in versions if x >= min_version]

    oldest = first(versions)
    newest = last(versions)

    # GraphiQL interface redirect
    @app.get("/graphql")
    async def redirect_to_latest_graphiql() -> RedirectResponse:
        """Redirect unversioned GraphiQL so developers can pin to the newest version."""
        return RedirectResponse(f"/graphql/v{newest}")


    imported = set()

    @app.middleware("http")
    async def graphql_loader(request: Request, call_next):
        graphql_match = re.match(r"/graphql/v(\d+)", request.url.path)
        if graphql_match is None:
            return await call_next(request)

        version_number = int(graphql_match.group(1))
        if version_number in imported:
            return await call_next(request)

        # Removed GraphQL versions send 410
        if 0 < version_number <= oldest:
            raise HTTPException(
                    status_code=400, detail={"message": "Removed GraphQL version"}
            )

        logger.info("Importing GraphQL version", version=version_number, imported=imported)

        start_time = time.monotonic()
        version = importlib.import_module(f"mora.graphapi.versions.v{version_number}.version").GraphQLVersion
        duration = time.monotonic() - start_time
        logger.info("Imported GraphQL router", version=version_number, duration=duration)

        # TODO: Add deprecation header as per the decision log (link/successor)
        start_time = time.monotonic()
        app.include_router(
            prefix=f"/graphql/v{version_number}",
            router=version.get_router(is_latest=version_number is newest),
        )
        duration = time.monotonic() - start_time
        logger.info("Mounted GraphQL router", version=version_number, duration=duration)

        imported.add(version_number)

        return await call_next(request)

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
