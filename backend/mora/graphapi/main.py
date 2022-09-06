# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from more_itertools import first
from more_itertools import last
from starlette import status
from starlette.responses import RedirectResponse
from starlette.responses import Response

from .versions.v1.version import GraphQLVersion1
from mora.auth.keycloak.oidc import auth

versions = [
    # Latest is never exposed directly, forcing clients to pin to a specific version
    GraphQLVersion1,
]


def setup_graphql(app: FastAPI, enable_graphiql: bool = False) -> None:
    router = APIRouter()

    oldest = first(versions)
    latest = last(versions)

    # GraphiQL interface redirect
    @router.get("")
    async def redirect_to_latest_graphiql() -> RedirectResponse:
        """Redirect unversioned GraphiQL so developers can pin to the newest version."""
        return RedirectResponse(f"/graphql/v{latest.version}")

    # Active routers
    active_versions = (
        v
        for v in versions
        if v.deprecation_date is None or v.deprecation_date > date.today()
    )
    for version in active_versions:
        # TODO: Add deprecation header as per the decision log (link/successor)
        router.include_router(version.get_router(graphiql=enable_graphiql))

    # Deprecated routers. This works as a fallback for all inactive version numbers,
    # since has lower routing priority by being defined later.
    @router.get("/v{version_number}", status_code=status.HTTP_404_NOT_FOUND)
    @router.post("/v{version_number}", status_code=status.HTTP_404_NOT_FOUND)
    async def non_existent(response: Response, version_number: int) -> None:
        """Return 404/410 properly depending on the requested version."""
        if 0 < version_number < oldest.version:
            response.status_code = status.HTTP_410_GONE

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)

    # Bind main router to the FastAPI app. Ideally, we'd let the caller define the
    # prefix, but this causes issues when routing the "empty" `/graphql` path.
    app.include_router(router, prefix="/graphql", dependencies=[Depends(auth)])

    # The legacy router is included last, so it only defines routes that have not
    # already been defined, i.e. POST /graphql.
    # TODO: This should be removed ASAP when everything is migrated
    app.include_router(
        oldest.get_router(path="/graphql"),
        deprecated=True,
        dependencies=[Depends(auth)],
    )
