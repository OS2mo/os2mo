# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather

from fastapi import APIRouter
from fastapi import HTTPException
from starlette.status import HTTP_204_NO_CONTENT

from mora.graphapi.health import health_map

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
    identifiers = list(health_map)
    statuses = await gather(*(health_map[identifier]() for identifier in identifiers))
    return dict(zip(identifiers, statuses, strict=True))


@router.get("/{identifier}")
async def healthcheck(identifier: str) -> bool | None:
    if identifier not in health_map:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Healthcheck not found")
    return await health_map[identifier]()
