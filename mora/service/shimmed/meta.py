# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from mora import config
from mora import exceptions


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():  # pragma: no cover
        settings = config.get_settings()
        return {
            "mo_hash": settings.commit_sha,
            "mo_version": settings.commit_tag,
            # MO and LoRa are shipped and versioned together
            "lora_version": settings.commit_tag,
        }

    @router.get("/saml/sso/")
    async def old_auth():  # pragma: no cover
        return RedirectResponse(url="/")

    return router


def service_catchall_router():
    router = APIRouter()

    @router.get("/service/{rest_of_path:path}")
    async def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router
