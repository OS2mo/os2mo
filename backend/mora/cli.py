# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# pragma: no cover file
"""Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.
"""

# TODO: Do we wanna access-log database access from here?
import asyncio
import sys
import time

import click
from fastramqpi.ra_utils.async_to_sync import async_to_sync
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.mo import MOAMQPSystem
from oio_rest.config import get_settings as oio_rest_get_settings
from sqlalchemy import select
from sqlalchemy import update
from structlog import get_logger

from mora.amqp import start_event_generator
from mora.db import AMQPSubsystem
from mora.db import create_sessionmaker

from . import amqp as amqp_subsystem
from . import config
from . import log

logger = get_logger()
settings = config.get_settings()
oio_rest_settings = oio_rest_get_settings()
sessionmaker = create_sessionmaker(
    user=oio_rest_settings.db_user,
    password=oio_rest_settings.db_password,
    host=oio_rest_settings.db_host,
    name=oio_rest_settings.db_name,
)


@click.group()
def cli():
    pass


_SLEEPING_TIME = 0.5


def _wait_for_service(name, wait_fn, unavailable_exception, wait):
    attempts = int(wait // _SLEEPING_TIME) or 1
    for i in range(1, attempts + 1):
        try:
            wait_fn()
            return int(wait - (i * _SLEEPING_TIME))
        except unavailable_exception:
            if i >= attempts:
                logger.error(f"{name} is unavailable. Exiting.")
                sys.exit(1)
            logger.info(f"{name} is unavailable - attempt {i}/{attempts}")
            time.sleep(_SLEEPING_TIME)


@cli.command()
@click.option(
    "--seconds",
    default=_SLEEPING_TIME,
    type=int,
    help="Wait up to n seconds for rabbitmq.",
)
def wait_for_rabbitmq(seconds):
    if not settings.amqp_enable:
        logger.info("AMQP is disabled. MO will not send messages.")
        return 0

    @async_to_sync
    async def connector():
        amqp_system = MOAMQPSystem(settings.amqp)
        await amqp_system.start()
        status = amqp_system.healthcheck()
        await amqp_system.stop()

        if status is False:
            raise ValueError("AMQP not healthy!")

    _wait_for_service(
        "RabbitMQ",
        connector,
        (ValueError, ConnectionError),
        seconds,
    )
    return 8


@cli.group()
def amqp():
    """Commands for the event generator and AMQP subsystem."""


async def _set_last_run(date):
    async with sessionmaker() as session:
        async with session.begin():
            await session.execute(
                update(AMQPSubsystem),
                [
                    {"id": 1, "last_run": date},
                ],
            )
            click.echo(f"Set last_run to {date}")


@amqp.command()
@click.argument("object-type", type=click.Choice(amqp_subsystem.MO_TYPE.__args__))
@click.argument("uuid", type=click.UUID)
def send_event(object_type, uuid) -> None:
    """Send AMQP event with routing_key=object_type and uuid as body."""
    amqp_system = AMQPSystem(settings.amqp)

    async def _send_event():
        async with sessionmaker() as session, session.begin():
            try:
                await amqp_system.start()
                await amqp_subsystem._send_amqp_message(
                    session, amqp_system, object_type, uuid
                )
            finally:
                await amqp_system.stop()

    asyncio.run(_send_event())


@amqp.command()
@click.argument("date")
def schedule_since(date) -> None:
    """Send all AMQP events that would be sent, had we not been sending events since *date*."""
    asyncio.run(_set_last_run(date))


@amqp.command()
def schedule_all() -> None:
    """Send an AMQP events for each object-type/UUID pair OS2MO knows of.

    Most event-driven integrations implement a /trigger/all-endpoint, that you
    may want to use instead of this hammer."""
    asyncio.run(_set_last_run("0001-01-01"))


@amqp.command()
def last_run() -> None:
    """Print last time the AMQP trigger checked for new events to send."""

    async def print_last_run():
        async with sessionmaker() as session:
            async with session.begin():
                last_run = await session.scalar(
                    select(AMQPSubsystem.last_run).where(AMQPSubsystem.id == 1)
                )
                click.echo(last_run)

    asyncio.run(print_last_run())


@amqp.command()
def start() -> None:
    """Start the event generator."""
    asyncio.run(start_event_generator(sessionmaker))


if __name__ == "__main__":
    log.init(settings.log_level, json=False)
    cli(prog_name="mora.cli")
