# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

"""
import asyncio
import sys
import time
from pathlib import Path

import click
from more_itertools import last
from ra_utils.async_to_sync import async_to_sync
from ramqp import AMQPSystem
from sqlalchemy import select
from sqlalchemy import update
from strawberry.cli.commands.codegen import _load_plugins
from strawberry.cli.commands.codegen import ConsolePlugin
from strawberry.codegen import QueryCodegen
from strawberry.printer import print_schema
from structlog import get_logger

from . import amqp as amqp_subsystem
from . import config
from . import log
from mora.db import AMQPSubsystem
from mora.db import get_sessionmaker
from mora.graphapi.main import graphql_versions
from oio_rest.config import get_settings as oio_rest_get_settings


logger = get_logger()
settings = config.get_settings()
oio_rest_settings = oio_rest_get_settings()
sessionmaker = get_sessionmaker(
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

    # XXX: Has to live here to avoid issues building documentation:
    # TypeError: metaclass conflict: the metaclass of a derived class must be a
    #            (non-strict) subclass of the metaclasses of all its bases.
    # Fun!
    from mora.triggers.internal.amqp_trigger import amqp_system
    from mora.triggers.internal.amqp_trigger import start_amqp
    from mora.triggers.internal.amqp_trigger import stop_amqp

    @async_to_sync
    async def connector():
        await start_amqp()
        status = amqp_system.healthcheck()
        await stop_amqp()

        if status is False:
            raise ValueError("AMQP not healthy!")

    _wait_for_service(
        "RabbitMQ",
        connector,
        (ValueError, ConnectionError),
        seconds,
    )
    return 8


@cli.command()
def export_schema() -> None:
    """Export GraphQL Schema in the GraphQL schema definition language (SDL).

    See https://strawberry.rocks/docs/guides/schema-export.
    """
    latest = last(graphql_versions)
    print(print_schema(latest.schema.get()))


@cli.command()
@click.option(
    "--output-dir",
    "-o",
    default=".",
    help="Output directory",
    type=click.Path(path_type=Path, exists=False, dir_okay=True, file_okay=False),
)
@click.argument("query", type=click.Path(path_type=Path, exists=True))
def codegen(
    output_dir: Path,
    query: Path,
) -> None:
    """Generate Python code from a GraphQL query based on the latest schema.

    See https://strawberry.rocks/docs/codegen/query-codegen.
    """

    latest = last(graphql_versions)
    schema = latest.schema.get()

    plugins = _load_plugins(["python"])
    plugins.append(ConsolePlugin(query, output_dir, plugins))

    code_generator = QueryCodegen(schema, plugins=plugins)
    code_generator.run(query.read_text())


@cli.group()
def amqp():
    """Commands for the AMQP subsystem."""


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
    amqp_system = AMQPSystem()

    async def _send_event():
        try:
            await amqp_system.start()
            await amqp_subsystem._send_amqp_message(amqp_system, object_type, uuid)
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


if __name__ == "__main__":
    log.init(settings.log_level, json=False)
    cli(prog_name="mora.cli")
