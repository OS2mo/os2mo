# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from dataclasses import dataclass
from httpx import AsyncClient

from mora import config


@dataclass
class Clients:
    mo: AsyncClient = AsyncClient()
    lora: AsyncClient = AsyncClient()

    async def init_clients(self):
        self.mo = AsyncClient(timeout=config.get_settings().httpx_timeout)
        # TODO: Setup AuthenticatedAsyncHTTPXClient when dependencies are fixed
        self.lora = AsyncClient(
            timeout=config.get_settings().httpx_timeout,
        )

    async def close_clients(self):
        await self.mo.aclose()
        await self.lora.aclose()


clients: Clients = Clients()
