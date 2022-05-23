#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi import APIRouter

from .errors import handle_gql_error
from mora import exceptions
from mora.graphapi.shim import execute_graphql

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():
        query = """
        query VersionQuery {
          version {
            mo_hash
            lora_version
            mo_version
          }
        }
        """

        # Execute GraphQL query to fetch required data
        response = await execute_graphql(query)
        handle_gql_error(response)

        return response.data["version"]

    @router.get("/service/{rest_of_path:path}")
    def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router