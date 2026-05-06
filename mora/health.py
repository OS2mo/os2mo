# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from fastapi import HTTPException
from more_itertools import one
from starlette.status import HTTP_204_NO_CONTENT

from mora.graphapi.shim import execute_graphql

router = APIRouter()


@router.get("/live", status_code=HTTP_204_NO_CONTENT)
async def liveness():
    """
    Endpoint to be used as a liveness probe for Kubernetes
    """


@router.get("/ready", status_code=HTTP_204_NO_CONTENT)
async def readiness():
    """
    Endpoint to be used as a readiness probe for Kubernetes.
    """


@router.get("/")
async def root() -> dict[str, bool]:
    query = """
    query HealthQuery {
      healths {
        objects {
          identifier
          status
        }
      }
    }
    """
    r = await execute_graphql(query)
    if r.errors:
        raise ValueError(r.errors)

    return {
        health["identifier"]: health["status"]
        for health in r.data["healths"]["objects"]
    }


@router.get("/{identifier}")
async def healthcheck(identifier: str) -> bool | None:
    query = """
    query HealthQuery($identifier: String!) {
      healths(filter: {identifiers: [$identifier]}) {
        objects {
          status
        }
      }
    }
    """

    r = await execute_graphql(query, variable_values={"identifier": identifier})
    if r.errors:
        raise ValueError(r.errors)
    if not r.data["healths"]["objects"]:
        raise HTTPException(status_code=404, detail="Healthcheck not found")
    return one(r.data["healths"]["objects"])["status"]
