# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import click  # pragma: no cover

from oio_rest.db import db_templating  # pragma: no cover


@click.group()
def cli():  # pragma: no cover
    """Management script for OIO REST."""


@cli.command()
@click.option("-o", "--output", type=click.File("wt"), default="-")
def sql(output):  # pragma: no cover
    """Write database SQL structure to standard output"""

    for line in db_templating.get_sql():
        output.write(line)
        output.write("\n")


if __name__ == "__main__":  # pragma: no cover
    cli()
