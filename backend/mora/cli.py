# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

'''

import logging
import os
import time

import click
import flask
import psycopg2
import sqlalchemy
import sys

from . import settings
from . import app as mora_app
from .service import configuration_options


logger = logging.getLogger(__name__)

group = flask.cli.FlaskGroup(help=__doc__, context_settings={
    'help_option_names': ['-h', '--help'],
})


_SLEEPING_TIME = 0.25
@group.command()
@click.option("--wait", default=_SLEEPING_TIME, type=int,
              help="Wait up to n seconds for the database connection before"
                   " exiting.")
def initdb(wait):
    """Initialize database.

    This is supposed to be idempotent, so you can run it without fear
    on an already initialized database.
    """

    def get_init_sessions():
        app = mora_app.create_app()

        def init_sessions():
            with app.app_context():
                app.session_interface.db.create_all()

        return init_sessions

    time_left = _wait_for_service(
        "Configuration database",
        configuration_options.create_db_table,
        psycopg2.OperationalError,
        wait,
    )
    if settings.SAML_AUTH_ENABLE:
        _wait_for_service("Sessions database", get_init_sessions(),
                          sqlalchemy.exc.OperationalError, time_left)


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
    success, error_msg = configuration_options.health_check()
    if success:
        logger.info("Configuration database passed health check")
    else:
        logger.critical(error_msg)
        sys.exit(3)


@group.command()
@click.option("--seconds", default=_SLEEPING_TIME, type=int,
              help="Wait up to n seconds for rabbitmq.")
def wait_for_rabbitmq(seconds):
    if not settings.config["amqp"]["enable"]:
        logger.info("AMQP is disabled. MO will not send messages.")
        return 0

    import pika

    def connector():
        pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.config["amqp"]["host"],
                port=settings.config["amqp"]["port"],
                heartbeat=0,
            )
        )

    _wait_for_service(
        "rabbitmq",
        connector,
        pika.exceptions.ConnectionClosed,
        seconds,
    )

    return 8


if __name__ == '__main__':
    group(prog_name=os.getenv('FLASK_PROG_NAME', sys.argv[0]))
