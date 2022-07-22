from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from mora.graphapi.versions.v1.main import get_version as get_v1_version
from starlette.responses import RedirectResponse

from mora.auth.keycloak.oidc import auth
from mora.graphapi.versions.main import get_versions


def setup_graphql(app: FastAPI, enable_graphiql: bool = False) -> None:
    router = APIRouter()

    @router.get("")
    async def redirect_to_latest():
        return RedirectResponse("/graphql/v2")

    for version in get_versions(enable_graphiql=enable_graphiql):
        router.include_router(version.router, prefix=f"/v{version.version}")

    # Subscriptions could be implemented using our trigger system.
    # They could expose an eventsource to the WebUI, enabling the UI to be dynamically
    # updated with changes from other users.
    # For now however; it is left uncommented and unimplemented.
    # app.add_websocket_route("/subscriptions", graphql_app)
    app.include_router(router, prefix="/graphql", dependencies=[Depends(auth)])
    # The legacy router is included last, so it only defines routes that have not
    # already been defined, i.e. POST /graphql.
    app.include_router(get_v1_version(enable_graphiql).router, prefix="/graphql", deprecated=True)  # fuck it
