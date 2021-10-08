# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

'''

import os
import sys
import time

import click
import sqlalchemy

from structlog import get_logger
from mora.async_util import async_to_sync

from mora.conf_db import create_db_table

from . import conf_db, config

logger = get_logger()


@click.group()
def group():
    pass


_SLEEPING_TIME = 0.25


@group.command()
def use_conf_db():
    settings = config.get_settings()
    if settings.conf_db_use:
        sys.exit(0)
    sys.exit(1)


@group.command()
@click.option("--wait", default=_SLEEPING_TIME, type=int,
              help="Wait up to n seconds for the database connection before"
                   " exiting.")
def initdb(wait):
    """Initialize database.

    This is supposed to be idempotent, so you can run it without fear
    on an already initialized database.
    """
    create_db_table()


@group.command()
@click.option("--wait", default=_SLEEPING_TIME, type=int,
              help="Wait up to n seconds for the database connection before"
                   " exiting.")
def checkdb(wait):
    """Check that database is online."""

    def check_db():
        with conf_db._get_session() as session:
            session.execute("SELECT 1")

    _wait_for_service("Database is up", check_db,
                      sqlalchemy.exc.OperationalError, wait)


def _wait_for_service(name, wait_fn, unavailable_exception, wait):
    attempts = int(wait // _SLEEPING_TIME) or 1
    for i in range(1, attempts + 1):
        try:
            wait_fn()
            return int(wait - (i * _SLEEPING_TIME))
        except unavailable_exception:
            click.echo(
                "%s is unavailable - attempt %s/%s" % (name, i, attempts))
            if i >= attempts:
                sys.exit(1)
            time.sleep(_SLEEPING_TIME)


@group.command()
def check_configuration_db_status():
    success, error_msg = conf_db.health_check()
    if success:
        logger.info("Configuration database passed health check")
    else:
        logger.critical("Config database failed health check", error_msg=error_msg)
        sys.exit(3)


@group.command()
@click.option("--seconds", default=_SLEEPING_TIME, type=int,
              help="Wait up to n seconds for rabbitmq.")
def wait_for_rabbitmq(seconds):
    settings = config.get_settings()
    if not settings.amqp_enable:
        logger.info("AMQP is disabled. MO will not send messages.")
        return 0

    # XXX: Has to live here to avoid issues building documentation:
    # TypeError: metaclass conflict: the metaclass of a derived class must be a
    #            (non-strict) subclass of the metaclasses of all its bases.
    # Fun!
    from mora.triggers.internal import amqp_trigger

    @async_to_sync
    async def connector():
        connection_pool, _ = await amqp_trigger.get_connection_pools()
        async with connection_pool.acquire() as connection:
            if not connection:
                raise ValueError("AMQP connection not found")
            if connection.is_closed:
                raise ValueError("AMQP connection is closed")

    _wait_for_service(
        "rabbitmq",
        connector,
        ValueError,
        seconds,
    )
    return 8


if __name__ == '__main__':
    group(prog_name=os.getenv('FLASK_PROG_NAME', sys.argv[0]))
