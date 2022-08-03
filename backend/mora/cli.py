# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

"""
import os
import sys
import time

import click
from ra_utils.async_to_sync import async_to_sync
from structlog import get_logger

from . import config
from . import log

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


if __name__ == "__main__":
    log.init(config.get_settings().log_level, json=False)
    group(prog_name=os.getenv("FLASK_PROG_NAME", sys.argv[0]))
