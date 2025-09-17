# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os

from alembic import command
from alembic import op
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker


async def run_async_upgrade(async_engine: AsyncEngine) -> None:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio

    def run_upgrade(connection) -> None:
        config_path = os.environ["ALEMBIC_CONFIG"]
        config = Config(config_path)
        config.attributes["connection"] = connection
        command.upgrade(config, "head")

    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade)


def apply_sql_from_file(relpath: str) -> None:
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "alembic", "versions", relpath
    )
    with open(path) as sql:
        Session = sessionmaker()
        bind = op.get_bind()
        session = Session(bind=bind)
        session.execute(text(sql.read()))
