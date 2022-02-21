# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from httpx import AsyncClient

# from raclients.auth import AuthenticatedAsyncHTTPXClient

from mora import config


client = AsyncClient(timeout=config.get_settings().httpx_timeout)


# TODO: Setup when dependencies are fixed
# def create_lora_client():
#     return AuthenticatedAsyncHTTPXClient(
#         client_id=config.get_settings().lora_client_id,
#         client_secret=config.get_settings().lora_client_secret,
#         auth_server=config.get_settings().lora_auth_server,
#         auth_realm=config.get_settings().lora_auth_realm,
#     )


# lora_client = create_lora_client()
lora_client = AsyncClient(
    base_url=config.get_settings().lora_url, timeout=config.get_settings().httpx_timeout
)
