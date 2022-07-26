# SPDX-FileCopyrightText: 2015-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from fastapi import APIRouter
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from oio_rest.custom_exceptions import DBException
from oio_rest.db import object_exists

kubernetes_router = APIRouter(prefix="/kubernetes")
_UUID_DUMMY = "00000000-0000-0000-0000-000000000000"


@kubernetes_router.get("/live", status_code=HTTP_204_NO_CONTENT)
async def liveness():
    """
    Endpoint to be used as a liveness probe for Kubernetes
    """
    return


@kubernetes_router.get("/ready", status_code=HTTP_204_NO_CONTENT)
async def readiness(response: Response):
    try:
        object_exists("Organisation", _UUID_DUMMY)
    except DBException:
        response.status_code = HTTP_503_SERVICE_UNAVAILABLE
