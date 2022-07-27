# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from dataclasses import dataclass

from fastapi import FastAPI
from httpx import AsyncClient

from mora import config


@dataclass
class Clients:
    mo: AsyncClient = AsyncClient()
    lora: AsyncClient = AsyncClient()

    async def init_clients(self, app: FastAPI):
        settings = config.get_settings()
        self.mo = AsyncClient(app=app, timeout=settings.httpx_timeout)
        # TODO: Setup AuthenticatedAsyncHTTPXClient when dependencies are fixed
        self.lora = AsyncClient(
            app=app if settings.enable_internal_lora else None,
            base_url=settings.lora_url,
            timeout=settings.httpx_timeout,
        )

    async def close_clients(self):
        await self.mo.aclose()
        await self.lora.aclose()


clients: Clients = Clients()
