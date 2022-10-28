# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Event handling."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import APIRouter
from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI
from ldap3 import Connection

from .config import Settings
from .dataloaders import configure_dataloaders
from .ldap import ad_healthcheck
from .ldap import configure_ad_connection


logger = structlog.get_logger()
fastapi_router = APIRouter()


@asynccontextmanager
async def open_ad_connection(ad_connection: Connection) -> AsyncIterator[None]:
    """Open the AD connection during FastRAMQPI lifespan.

    Yields:
        None
    """
    with ad_connection:
        yield


@asynccontextmanager
async def seed_dataloaders(fastramqpi: FastRAMQPI) -> AsyncIterator[None]:
    """Seed dataloaders during FastRAMQPI lifespan.

    Yields:
        None
    """
    logger.info("Seeding dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)
    yield


def create_fastramqpi(**kwargs: Any) -> FastRAMQPI:
    """FastRAMQPI factory.

    Returns:
        FastRAMQPI system.
    """
    logger.info("Retrieving settings")
    settings = Settings(**kwargs)

    logger.info("Setting up FastRAMQPI")
    fastramqpi = FastRAMQPI(application_name="ad2mosync", settings=settings.fastramqpi)
    fastramqpi.add_context(settings=settings)

    logger.info("Configuring AD connection")
    ad_connection = configure_ad_connection(settings)
    fastramqpi.add_context(ad_connection=ad_connection)
    fastramqpi.add_healthcheck(name="ADConnection", healthcheck=ad_healthcheck)
    fastramqpi.add_lifespan_manager(open_ad_connection(ad_connection), 1500)

    fastramqpi.add_lifespan_manager(seed_dataloaders(fastramqpi), 2000)

    logger.info("Configuring Dataloaders")
    context = fastramqpi.get_context()
    dataloaders = configure_dataloaders(context)
    fastramqpi.add_context(dataloaders=dataloaders)

    return fastramqpi


def create_app(**kwargs: Any) -> FastAPI:
    """FastAPI application factory.

    Returns:
        FastAPI application.
    """
    fastramqpi = create_fastramqpi(**kwargs)

    app = fastramqpi.get_app()
    app.include_router(fastapi_router)

    @app.get("/all", status_code=202)
    async def load_all_org_persons() -> Any:
        """Request all organizational persons"""
        logger.info("Manually triggered request of all organizational persons")

        result = await fastramqpi._context["user_context"][
            "dataloaders"
        ].org_persons_loader.load(1)
        return result

    return app
