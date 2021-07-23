# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter

from mora import config


def keycloak_config_router():
    settings = config.get_settings()
    router = APIRouter()

    @router.get("/keycloak.json")
    def get_config():
        return {
            "realm": "mo",
            "auth-server-url": settings.keycloak_auth_server_url,
            "ssl-required": settings.keycloak_ssl_required,
            "resource": "mo",
            "public-client": True,
            "confidential-port": 0,
        }

    return router
