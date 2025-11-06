# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from mora import exceptions
from mora.graphapi.shim import execute_graphql

from .errors import handle_gql_error


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():  # pragma: no cover
        query = """
        query VersionQuery {
          version {
            mo_hash
            mo_version
            lora_version
          }
        }
        """

        # Execute GraphQL query to fetch required data
        response = await execute_graphql(query)
        handle_gql_error(response)

        return response.data["version"]

    @router.get("/service/{rest_of_path:path}")
    async def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    @router.get("/saml/sso/")
    async def old_auth():  # pragma: no cover
        return RedirectResponse(url="/")

    return router
