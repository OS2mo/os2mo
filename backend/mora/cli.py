# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

"""
import os
import sys
import time
from pathlib import Path

import click
from more_itertools import last
from ra_utils.async_to_sync import async_to_sync
from strawberry.cli.commands.codegen import _load_plugins
from strawberry.cli.commands.codegen import ConsolePlugin
from strawberry.codegen import QueryCodegen
from strawberry.printer import print_schema
from structlog import get_logger

from . import config
from . import log
from mora.graphapi.main import graphql_versions

logger = get_logger()


@click.group()
def group():
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


@group.command()
@click.option(
    "--seconds",
    default=_SLEEPING_TIME,
    type=int,
    help="Wait up to n seconds for rabbitmq.",
)
def wait_for_rabbitmq(seconds):
    settings = config.get_settings()
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


@group.command()
def export_schema() -> None:
    """Export GraphQL Schema in the GraphQL schema definition language (SDL).

    See https://strawberry.rocks/docs/guides/schema-export.
    """
    latest = last(graphql_versions)
    print(print_schema(latest.schema.get()))


@group.command()
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


if __name__ == "__main__":
    log.init(config.get_settings().log_level, json=False)
    group(prog_name=os.getenv("FLASK_PROG_NAME", sys.argv[0]))
