# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from async_lru import alru_cache
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import UUID as PgUUID

import mora.db
from mora.db import OrganisationFunktionRegistrering

METRIC_MAX_DAILY_REGISTRATIONS_SINGLE_ORG_FUNC = Gauge(
    "os2mo_max_daily_registrations_single_org_func",
    "Highest number of registrations made on a single organisation function "
    "by a single actor within the last day",
    ["actor"],
)


@alru_cache(ttl=24 * 60 * 60)  # Cache for 24h
async def max_daily_registrations_single_org_func(info: Info) -> None:
    """Set METRIC_MAX_DAILY_REGISTRATIONS_SINGLE_ORG_FUNC from the database.

    Instrumentator callback, called on every request, so it only does work when
    the metrics endpoint is scraped.
    """
    url_path = info.request.url.path
    if not (url_path.endswith("metrics") or url_path.endswith("metrics/")):
        return

    METRIC_MAX_DAILY_REGISTRATIONS_SINGLE_ORG_FUNC.clear()

    async with (
        mora.db._get_sessionmaker(info.request)() as session,
        session.begin(),
    ):
        # The actor lives inside the `registrering` composite column, which the
        # ORM does not map, so it has to be spelled out.
        actor = type_coerce(text("(registrering).brugerref"), PgUUID)
        count = func.count()
        query = (
            select(
                OrganisationFunktionRegistrering.organisationfunktion_id,
                actor,
                count,
            )
            .where(
                func.now()
                - func.lower(OrganisationFunktionRegistrering.registrering_period)
                < func.make_interval(days=1)
            )
            .group_by(OrganisationFunktionRegistrering.organisationfunktion_id, actor)
            .order_by(count.desc())
            .limit(1)
        )

        result = await session.execute(query)
        row = result.first()

        # Report zero, with no actor to attribute it to, so the dataseries goes
        # to zero instead of disappearing when nobody has registered anything.
        _, brugerref, registrations = row if row is not None else (None, "", 0)

        METRIC_MAX_DAILY_REGISTRATIONS_SINGLE_ORG_FUNC.labels(actor=brugerref).set(
            registrations
        )


def setup_registration_metrics(instrumentator: Instrumentator) -> None:
    instrumentator.add(max_daily_registrations_single_org_func)
