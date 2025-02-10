# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from textwrap import dedent
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastramqpi.ramqp import AMQPSystem
from starlette.responses import PlainTextResponse
from starlette.responses import RedirectResponse
from strawberry.printer import print_schema

from mora import db
from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.graphapi.custom_router import CustomGraphQLRouter
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from mora.graphapi.versions.latest.audit import get_audit_loaders
from mora.graphapi.versions.latest.dataloaders import get_loaders

router = APIRouter()


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


def get_router(version: Version) -> APIRouter:
    """Get Strawberry FastAPI router serving this GraphQL API version."""
    schema = get_schema(version)
    router = CustomGraphQLRouter(
        graphql_ide="graphiql",  # TODO: pathfinder seems a lot nicer
        schema=schema,
        context_getter=get_context,
    )

    @router.get("/schema.graphql", response_class=PlainTextResponse)
    async def sdl() -> str:
        """Return the GraphQL version's schema definition in SDL format."""
        header = dedent(
            f"""\
            # SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
            # SPDX-License-Identifier: MPL-2.0
            #
            # OS2mo GraphQL API schema definition (v{version.value}).
            # https://os2mo.eksempel.dk/graphql/v{version.value}/schema.graphql

            """
        )
        return header + print_schema(schema)

    return router


@router.get("/graphql")
@router.get("/graphql/")
async def redirect_to_latest_graphiql() -> RedirectResponse:
    """Redirect unversioned GraphiQL so developers can pin to the newest version."""
    return RedirectResponse(f"/graphql/v{LATEST_VERSION.value}")


for version in Version:
    router.include_router(
        prefix=f"/graphql/v{version.value}", router=get_router(version)
    )
