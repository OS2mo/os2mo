# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import importlib
import re
from functools import cache
from typing import Any

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from structlog.stdlib import get_logger

logger = get_logger()

graphql_versions = [
    # TODO: remove ...
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    # TODO: ... remove
    17,
    18,
    19,
    20,
    21,
    22,
]
latest_graphql_version = max(graphql_versions)


@cache
def load_graphql_version(version_number: int) -> APIRouter:
    """Dynamically import and load the specified GraphQL version.

    Note:
        This function should only ever be called once for each version_number.

    Args:
        version_number: The version number of the GraphQL version to load.

    Returns:
        A FastAPI APIRouter for the given GraphQL version.
    """
    assert version_number in graphql_versions

    version = importlib.import_module(
        f"mora.graphapi.versions.v{version_number}.version"
    ).GraphQLVersion
    # TODO: Add deprecation header as per the decision log (link/successor)
    router = version.get_router(is_latest=version_number is latest_graphql_version)
    return router


def setup_graphql(app: FastAPI) -> None:
    """Setup our GraphQL endpoints on FastAPI.

    Note:
        GraphQL version endpoints are dynamically loaded.

    Args:
        app: The FastAPI to load GraphQL endpoints on.
    """

    @app.get("/graphql")
    @app.get("/graphql/")
    async def redirect_to_latest_graphiql() -> RedirectResponse:
        """Redirect unversioned GraphiQL so developers can pin to the newest version."""
        return RedirectResponse(f"/graphql/v{latest_graphql_version}")

    imported: set[int] = set()
    version_regex = re.compile(r"/graphql/v(\d+)")

    @app.middleware("http")
    async def graphql_loader(request: Request, call_next: Any) -> Any:
        graphql_match = version_regex.match(request.url.path)
        if graphql_match is None:
            return await call_next(request)

        version_number = int(graphql_match.group(1))
        if version_number in imported:
            return await call_next(request)

        # Non-existent GraphQL versions send 404
        if version_number not in graphql_versions:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "No such GraphQL version"},
            )

        logger.info(
            "Importing GraphQL version", version=version_number, imported=imported
        )
        router = load_graphql_version(version_number)
        app.include_router(prefix=f"/graphql/v{version_number}", router=router)
        imported.add(version_number)

        return await call_next(request)
