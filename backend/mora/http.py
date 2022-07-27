# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI
from httpx import AsyncClient

from mora import config


@dataclass
class Clients:
    lora: AsyncClient = AsyncClient()

    async def init_clients(self, app: Optional[FastAPI] = None):
        # TODO: Setup AuthenticatedAsyncHTTPXClient when dependencies are fixed
        self.lora = AsyncClient(
            app=app,
            base_url=config.get_settings().lora_url,
            timeout=config.get_settings().httpx_timeout,
        )

    async def close_clients(self):
        await self.lora.aclose()


clients: Clients = Clients()
