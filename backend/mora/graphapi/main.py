# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import importlib

import time
from fastapi import APIRouter
from fastapi import FastAPI
from more_itertools import first
from more_itertools import last
from starlette import status
from starlette.responses import RedirectResponse
from starlette.responses import Response
import structlog


logger = structlog.get_logger()

graphql_versions = list(range(2, 21))


def setup_graphql(
    app: FastAPI, min_version: int | None = None
) -> None:
    versions = graphql_versions

    if min_version is not None:
        versions = [x for x in versions if x >= min_version]

    router = APIRouter()

    oldest = first(versions)
    newest = last(versions)

    # GraphiQL interface redirect
    @router.get("")
    async def redirect_to_latest_graphiql() -> RedirectResponse:
        """Redirect unversioned GraphiQL so developers can pin to the newest version."""
        return RedirectResponse(f"/graphql/v{newest}")

    logger.info("Loading GraphQL")

    # Active routers
    for version_number in reversed(versions):
        start_time = time.monotonic()
        version = importlib.import_module(f"mora.graphapi.versions.v{version_number}.version").GraphQLVersion
        duration = time.monotonic() - start_time
        logger.info("Imported GraphQL router", version=version.version, duration=duration)

        # TODO: Add deprecation header as per the decision log (link/successor)
        start_time = time.monotonic()
        router.include_router(
            prefix=f"/v{version.version}",
            router=version.get_router(is_latest=version is newest),
        )
        duration = time.monotonic() - start_time
        logger.info("Mounted GraphQL router", version=version.version, duration=duration)

    # Deprecated routers. This works as a fallback for all inactive version numbers,
    # since has lower routing priority by being defined later.
    @router.get("/v{version_number}", status_code=status.HTTP_404_NOT_FOUND)
    @router.post("/v{version_number}", status_code=status.HTTP_404_NOT_FOUND)
    async def non_existent(response: Response, version_number: int) -> None:
        """Return 404/410 properly depending on the requested version."""
        if 0 < version_number <= oldest:
            response.status_code = status.HTTP_410_GONE

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)

    # Bind main router to the FastAPI app. Ideally, we'd let the caller define the
    # prefix, but this causes issues when routing the "empty" `/graphql` path.
    app.include_router(router, prefix="/graphql")
