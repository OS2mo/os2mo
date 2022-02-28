# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from httpx import AsyncClient

from mora import config


client = AsyncClient(timeout=config.get_settings().httpx_timeout)


# TODO: Setup AuthenticatedAsyncHTTPXClient when dependencies are fixed
lora_client = AsyncClient(
    base_url=config.get_settings().lora_url, timeout=config.get_settings().httpx_timeout
)
