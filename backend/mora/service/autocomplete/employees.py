# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from .shared import get_at_date_sql
# from sqlalchemy.sql import select
# from sqlalchemy.sql import union


async def search_employees(
    sessionmaker: async_sessionmaker, query: str, at: date | None = None
) -> [Row]:
    at_sql, at_sql_bind_params = get_at_date_sql(at)

    # async with sessionmaker() as session:
    #     selects = [
    #         select(cte.c.uuid)
    #         for cte in (
    #             _get_cte_uuid_hits(query, at_sql),
    #             # _get_cte_orgunit_name_hits(query, at_sql),
    #             # _get_cte_orgunit_addr_hits(query, at_sql),
    #             # _get_cte_orgunit_itsystem_hits(query, at_sql),
    #         )
    #     ]
    #     all_hits = union(*selects).cte()


def _get_cte_uuid_hits():
    pass
