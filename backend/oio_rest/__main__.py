# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import sys
import time

import click
import psycopg2

from oio_rest.db import db_templating
from oio_rest.db import get_connection
from oio_rest.db.alembic_helpers import is_alembic_installed
from oio_rest.db.alembic_helpers import is_schema_installed
from oio_rest.db.alembic_helpers import setup_database
from oio_rest.db.alembic_helpers import stamp_database
from oio_rest.db.alembic_helpers import truncate_all_tables


@click.group()
def cli():
    """Management script for OIO REST."""


@cli.command()
@click.option("-o", "--output", type=click.File("wt"), default="-")
def sql(output):
    """Write database SQL structure to standard output"""

    for line in db_templating.get_sql():
        output.write(line)
        output.write("\n")


@cli.command()
@click.option(
    "--wait",
    default=None,
    type=int,
    help="Wait up to n seconds for the database connection before exiting.",
)
def initdb(wait):
    """Initialize database.

    This is supposed to be idempotent, so you can run it without fear
    on an already initialized database.
    """
    SLEEPING_TIME = 0.25

    def check_connection():
        try:
            get_connection()
            return True
        except psycopg2.OperationalError as exp:
            print(exp)
            return False

    attempts = 1 if wait is None else int(wait // SLEEPING_TIME)

    for i in range(1, attempts + 1):
        if check_connection():
            break
        if i == attempts:
            sys.exit(1)
        click.echo(f"Postgres is unavailable - attempt {i}/{attempts}")
        time.sleep(SLEEPING_TIME)

    if is_schema_installed():
        click.echo("Detected existing LoRa database")
        # A "legacy" database without Alembic migrations is "stamped", meaning a "fake"
        # Alembic migration is installed, setting its migration level to 'initial'.
        if not is_alembic_installed():
            stamp_database()
            click.echo("Stamped existing LoRa database")
        # Apply Alembic migrations (= upgrade to latest migration)
        setup_database()
        click.echo("Upgraded LoRa database schema")
    else:
        setup_database()
        click.echo("Initialized LoRa database")


@cli.command()
def truncatedb():
    """Empty all tables in the database."""
    truncate_all_tables()


if __name__ == "__main__":
    cli()
