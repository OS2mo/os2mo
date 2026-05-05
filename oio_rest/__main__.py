# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# pragma: no cover file
import click

from oio_rest.db import db_templating


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


if __name__ == "__main__":
    cli()
