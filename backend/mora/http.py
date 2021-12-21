# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from httpx import AsyncClient
from raclients.auth import AuthenticatedAsyncHTTPXClient

from mora import config


client = AsyncClient(timeout=config.get_settings().httpx_timeout)

lora_client = AuthenticatedAsyncHTTPXClient(
    client_id=config.get_settings().lora_client_id,
    client_secret=config.get_settings().lora_client_secret,
    auth_server=config.get_settings().lora_auth_server,
    auth_realm=config.get_settings().lora_auth_realm,
)
