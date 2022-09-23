# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Response
from more_itertools import one
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.health import keycloak
from mora.graphapi.versions.latest.health import oio_rest


router = APIRouter()


@router.get("/live", status_code=HTTP_204_NO_CONTENT)
async def liveness():
    """
    Endpoint to be used as a liveness probe for Kubernetes
    """
    return


@router.get(
    "/ready",
    status_code=HTTP_204_NO_CONTENT,
    responses={
        "204": {"description": "Ready"},
        "503": {"description": "Not ready"},
    },
)
async def readiness(response: Response):
    """
    Endpoint to be used as a readiness probe for Kubernetes.
    If MO itself is ready (FastAPI is running), LoRa is running,
    and Keycloak all are healthy then MO is considered to be ready.
    """

    lora_ready, keycloak_ready = await asyncio.gather(oio_rest(), keycloak())

    if not (lora_ready and keycloak_ready):
        response.status_code = HTTP_503_SERVICE_UNAVAILABLE


@router.get("/")
async def root() -> dict[str, bool]:
    query = """
    query HealthQuery {
      healths {
        identifier
        status
      }
    }
    """
    r = await execute_graphql(query)
    if r.errors:
        raise ValueError(r.errors)

    return {health["identifier"]: health["status"] for health in r.data["healths"]}


@router.get("/{identifier}")
async def healthcheck(identifier: str) -> bool | None:
    query = """
    query HealthQuery($identifier: String!) {
      healths(identifiers: [$identifier]) {
        status
      }
    }
    """

    r = await execute_graphql(query, variable_values={"identifier": identifier})
    if r.errors:
        raise ValueError(r.errors)
    if not r.data["healths"]:
        raise HTTPException(status_code=404, detail="Healthcheck not found")
    return one(r.data["healths"])["status"]
