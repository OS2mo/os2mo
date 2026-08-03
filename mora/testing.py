# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import secrets
from contextlib import AbstractAsyncContextManager
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import APIRouter
from psycopg.errors import UndefinedTable
from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT
from structlog import get_logger

from mora import amqp
from mora import db
from mora import depends
from mora.service.org import ConfiguredOrganisation
from oio_rest.config import Settings as LoraSettings
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db.alembic_helpers import run_async_upgrade

logger = get_logger()


router = APIRouter()


@router.post("/amqp/emit", status_code=HTTP_204_NO_CONTENT)
async def emit(request: Request, amqp_system: depends.AMQPSystem) -> None:
    """
    Emit queued AMQP events immediately.

    Note that this is only needed for the "new" AMQP subsystem. Events in the old one
    are always sent immediately.
    """
    logger.warning("Emitting AMQP events")
    # TODO: replace the `while True` loop with:
    # await amqp._emit_events(session, amqp_system)
    # once everyone has had a chance to upgrade to FastRAMQPI v12.0.4+
    while True:
        try:
            # The request-wide database session, which is used in almost every other
            # endpoint, cannot be used here, as the database snapshot/rollback
            # forcefully closes all connections, irrevocably destroying the session.
            async with db._get_sessionmaker(request)() as session, session.begin():
                await amqp._emit_events(session, amqp_system)
            return
        except (OperationalError, ProgrammingError) as e:  # pragma: no cover
            if isinstance(e, ProgrammingError) and not isinstance(
                e.orig, UndefinedTable
            ):
                raise
            # The database is unavailable while being snapshot or restored. Retry until
            # we succeed.
            logger.warning("Error emitting AMQP events", error=e)
            await asyncio.sleep(0.5)


@router.post("/events/reset-last-tried", status_code=HTTP_204_NO_CONTENT)
async def reset_last_tried(session: depends.Session) -> None:
    """Reset the `last_tried` of GraphQL events.

    Normally, events which are fetched - but not acknowledged - are not retried
    (cannot be fetched) for three minutes, increasing exponentially. Resetting
    `last_tried` allows quick retrying during integration tests.
    """
    logger.warning("Resetting GraphQL events last_tried")
    await session.execute(
        update(db.Event).values(
            last_tried=datetime(1970, 1, 1),
        )
    )


@asynccontextmanager
async def superuser_connection(
    lora_settings: LoraSettings,
) -> AbstractAsyncContextManager[AsyncConnection]:
    """Managing databases requires a superuser connection."""
    engine = db.create_engine(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name="postgres",
    )
    # AUTOCOMMIT disables transactions to allow for create/drop database operations
    engine.update_execution_options(isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as connection:
            yield connection
    finally:
        await engine.dispose()


async def _terminate_database_connections(
    superuser: AsyncConnection, database: str
) -> None:
    await superuser.execute(
        text(
            f"""
            select pg_terminate_backend(pid)
            from pg_stat_activity
            where datname = '{database}' and pid <> pg_backend_pid()
            """
        )
    )


async def _set_database_connectable(
    superuser: AsyncConnection, database: str, allow: bool
) -> None:
    await superuser.execute(
        text(
            f"""
            update pg_database
            set datallowconn = :allow
            where datname = '{database}'
        """
        ),
        dict(allow=allow),
    )


async def copy_database(
    superuser: AsyncConnection, source: str, destination: str
) -> None:
    """Copy database, overwriting (dropping) destination if it already exists."""
    # Copy database to temporary staging database. This ensures no one will
    # attempt to connect to it while we are working on it.
    staging = f"staging_{secrets.token_hex(4)}"
    await superuser.execute(text(f"create database {staging} template {source}"))
    # Copying a database does not copy its configuration parameters. These statements
    # are copied from the initial alembic migration.
    await superuser.execute(
        text(f"ALTER DATABASE {staging} SET search_path = actual_state,public")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {staging} SET datestyle to 'ISO, YMD'")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {staging} SET intervalstyle to 'sql_standard'")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {staging} SET time zone 'Europe/Copenhagen'")
    )
    # Swap staging database in
    await superuser.execute(text(f"drop database if exists {destination} with (force)"))
    await superuser.execute(
        text(f"alter database {staging} rename to {destination}"),
    )


def _get_current_database(session: db.AsyncSession) -> str:
    return session.get_bind().engine.url.database


def _get_snapshot_database(session: db.AsyncSession) -> str:
    current_database = _get_current_database(session)
    return f"{current_database}_snapshot"


@router.post("/database/snapshot", status_code=HTTP_204_NO_CONTENT)
async def snapshot(session: depends.Session) -> None:
    """
    Snapshot the database.
    """
    logger.warning("Snapshotting database")
    source = _get_current_database(session)
    async with superuser_connection(lora_get_settings()) as superuser:
        # Unlike the other endpoints, we snapshot the database we are currently
        # connected to. A database cannot be used as a copy template while it has
        # connections, so disallow new connections and terminate existing.
        try:
            await _set_database_connectable(superuser, source, False)
            await _terminate_database_connections(superuser, source)
            await copy_database(
                superuser,
                source=source,
                destination=_get_snapshot_database(session),
            )
        finally:
            # Always allow connections again, so a failed snapshot does not leave
            # the database unusable.
            await _set_database_connectable(superuser, source, True)


@router.post("/database/restore", status_code=HTTP_204_NO_CONTENT)
async def restore(session: depends.Session) -> None:
    """
    Restore database snapshot.
    """
    logger.warning("Restoring database")
    async with superuser_connection(lora_get_settings()) as superuser:
        await copy_database(
            superuser,
            source=_get_snapshot_database(session),
            destination=_get_current_database(session),
        )
    ConfiguredOrganisation.clear()


EMPTY_DB_TEMPLATE = "empty_db_template"


@router.post("/database/setup", status_code=HTTP_204_NO_CONTENT)
async def setup() -> None:
    """
    Setup empty database for templating.
    """
    logger.warning("Setting up empty database template")
    lora_settings = lora_get_settings()

    async with superuser_connection(lora_settings) as superuser:
        await superuser.execute(
            text(f"drop database if exists {EMPTY_DB_TEMPLATE} with (force)")
        )
        await superuser.execute(text(f"create database {EMPTY_DB_TEMPLATE}"))

    # Apply alembic migrations
    engine = db.create_engine(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=EMPTY_DB_TEMPLATE,
    )
    try:
        await run_async_upgrade(engine)
    finally:
        await engine.dispose()


@router.post("/database/reset", status_code=HTTP_204_NO_CONTENT)
async def reset(session: depends.Session) -> None:
    """
    Reset database to a clean, migrated state with all tables empty.
    """
    logger.warning("Resetting database to empty")
    async with superuser_connection(lora_get_settings()) as superuser:
        await copy_database(
            superuser,
            source=EMPTY_DB_TEMPLATE,
            destination=_get_current_database(session),
        )
    ConfiguredOrganisation.clear()
