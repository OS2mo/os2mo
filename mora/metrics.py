# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info
from sqlalchemy import Text
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import type_coerce

import mora.db
from mora.amqp import _lora_to_mo
from mora.db import AsyncSession
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRegistrering
from oio_rest.db.db_structure import REAL_DB_STRUCTURE

METRIC_REGISTRATION_COUNT = Gauge(
    "os2mo_registration_count",
    "Number of registrations",
    ["type"],
)

METRIC_MAX_REGISTRATIONS_ON_OBJECT_24H_ORG_FUNC = Gauge(
    "os2mo_max_registrations_on_object_24h_org_func",
    "Highest number of registrations on a single organisation function within "
    "the last day",
    ["type"],
)

# Every LoRa object has a `<name>_registrering` table. Organisation functions
# are left out; they are counted per funktionsnavn instead.
LORA_OBJECTS = tuple(
    lora_object
    for lora_object in REAL_DB_STRUCTURE
    if lora_object != "organisationfunktion"
)


async def org_func_registration_count(session: AsyncSession) -> None:
    """Count organisation function registrations per funktionsnavn."""
    # `funktionsnavn` is mapped as an enum, but the column is really just text
    # and old databases hold values outside the enum, e.g. "Rolle". Read it as
    # text so such rows do not fail the whole scrape.
    funktionsnavn_column = type_coerce(
        OrganisationFunktionAttrEgenskaber.funktionsnavn, Text
    )
    query = select(
        funktionsnavn_column,
        func.count(
            OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
        ),
    ).group_by(funktionsnavn_column)

    result = await session.execute(query)
    for funktionsnavn, registrations in result.all():
        # `funktionsnavn` is an unconstrained text column, so fall back to the
        # LoRa name rather than dropping registrations we cannot map.
        type_ = _lora_to_mo.get(funktionsnavn, funktionsnavn.lower())
        METRIC_REGISTRATION_COUNT.labels(type=type_).set(registrations)


async def max_registrations_on_object_24h_org_func(session: AsyncSession) -> None:
    """Find the most edited organisation function of each funktionsnavn.

    A high value means a single object is being rewritten over and over, which
    is usually an integration looping rather than genuine editing.
    """
    # `funktionsnavn` is mapped as an enum, but the column is really just text
    # and old databases hold values outside the enum, e.g. "Rolle". Read it as
    # text so such rows do not fail the whole scrape.
    funktionsnavn_column = type_coerce(
        OrganisationFunktionAttrEgenskaber.funktionsnavn, Text
    )

    # Registrations per object, which the outer query takes the maximum of. A
    # registration can have several `attr_egenskaber` rows, one per virkning,
    # so count the registrations rather than the join:
    #
    # SELECT
    #     funktionsnavn,
    #     MAX(registration_count) AS max_count
    # FROM (
    #     SELECT
    #         funktionsnavn,
    #         organisationfunktion_id,
    #         COUNT(DISTINCT reg.id) AS registration_count
    #     FROM organisationfunktion_registrering AS reg
    #     JOIN organisationfunktion_attr_egenskaber AS attr
    #         ON reg.id = attr.organisationfunktion_registrering_id
    #     WHERE LOWER((registrering).timeperiod) > NOW() - INTERVAL '1 day'
    #     GROUP BY funktionsnavn, organisationfunktion_id
    # ) AS counts
    # GROUP BY funktionsnavn;

    counts = (
        select(
            funktionsnavn_column,
            OrganisationFunktionRegistrering.organisationfunktion_id,
            func.count(distinct(OrganisationFunktionRegistrering.id)).label(
                "registration_count"
            ),
        )
        .join(
            OrganisationFunktionAttrEgenskaber,
            OrganisationFunktionRegistrering.id
            == OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id,
        )
        .where(
            func.lower(OrganisationFunktionRegistrering.registrering_period)
            > func.now() - func.make_interval(days=1)
        )
        .group_by(
            funktionsnavn_column,
            OrganisationFunktionRegistrering.organisationfunktion_id,
        )
        .subquery("counts")
    )

    query = select(
        counts.c.funktionsnavn,
        func.max(counts.c.registration_count),
    ).group_by(counts.c.funktionsnavn)

    result = await session.execute(query)
    for funktionsnavn, max_count in result.all():
        # `funktionsnavn` is an unconstrained text column, so fall back to the
        # LoRa name rather than dropping registrations we cannot map.
        type_ = _lora_to_mo.get(funktionsnavn, funktionsnavn.lower())
        METRIC_MAX_REGISTRATIONS_ON_OBJECT_24H_ORG_FUNC.labels(type=type_).set(
            max_count
        )


async def object_registrations_count(session: AsyncSession) -> None:
    """Count registrations of every other LoRa object, one type at a time."""
    for lora_object in LORA_OBJECTS:
        query = select(func.count()).select_from(table(f"{lora_object}_registrering"))
        result = await session.execute(query)
        registrations = result.scalar_one()
        type_ = _lora_to_mo.get(lora_object, lora_object)
        METRIC_REGISTRATION_COUNT.labels(type=type_).set(registrations)


async def registration_count(info: Info) -> None:
    """Set METRIC_REGISTRATION_COUNT from the database.

    Instrumentator callback, called on every request, so it only does work when
    the metrics endpoint is scraped.
    """
    url_path = info.request.url.path
    if not (url_path.endswith("metrics") or url_path.endswith("metrics/")):
        return

    # Drop the children so types that disappear from the database stop being
    # reported with their stale count. Both counting functions share the metric,
    # so this has to happen once, before either of them runs.
    METRIC_REGISTRATION_COUNT.clear()
    METRIC_MAX_REGISTRATIONS_ON_OBJECT_24H_ORG_FUNC.clear()

    async with (
        mora.db._get_sessionmaker(info.request)() as session,
        session.begin(),
    ):
        await org_func_registration_count(session)
        await object_registrations_count(session)
        await max_registrations_on_object_24h_org_func(session)


def setup_registration_metrics(instrumentator: Instrumentator) -> None:
    instrumentator.add(registration_count)
