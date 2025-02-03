# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import importlib
import re
from collections.abc import Awaitable
from collections.abc import Callable
from functools import cache
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastramqpi.ramqp import AMQPSystem
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import RedirectResponse
from structlog.stdlib import get_logger

from mora import db
from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.graphapi.main import graphql_versions
from mora.graphapi.main import latest_graphql_version

from .versions.latest.audit import get_audit_loaders
from .versions.latest.dataloaders import get_loaders

logger = get_logger()


async def get_context(
    # NOTE: If you add or remove any parameters, make sure to keep the
    # execute_graphql parameters synchronised!
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter),
    amqp_system: AMQPSystem = Depends(depends.get_amqp_system),
    session: db.AsyncSession = Depends(db.get_session),
) -> dict[str, Any]:
    return {
        **await get_loaders(),
        "get_token": get_token,
        "amqp_system": amqp_system,
        "session": session,
        **get_audit_loaders(session),
    }


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
    router = version.get_router()
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
