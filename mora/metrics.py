# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import type_coerce

import mora.db
from mora.amqp import _lora_to_mo
from mora.db import AsyncSession
from mora.db import OrganisationFunktionAttrEgenskaber
from oio_rest.db.db_structure import REAL_DB_STRUCTURE

METRIC_REGISTRATION_COUNT = Counter(
    "os2mo_registration_count",
    "Number of registrations",
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
        METRIC_REGISTRATION_COUNT.labels(type=type_).inc(registrations)


async def object_registrations_count(session: AsyncSession) -> None:
    """Count registrations of every other LoRa object, one type at a time."""
    for lora_object in LORA_OBJECTS:
        query = select(func.count()).select_from(table(f"{lora_object}_registrering"))
        result = await session.execute(query)
        registrations = result.scalar_one()
        type_ = _lora_to_mo.get(lora_object, lora_object)
        METRIC_REGISTRATION_COUNT.labels(type=type_).inc(registrations)


async def registration_count(info: Info) -> None:
    """Set METRIC_REGISTRATION_COUNT from the database.

    Instrumentator callback, called on every request, so it only does work when
    the metrics endpoint is scraped.
    """
    url_path = info.request.url.path
    if not (url_path.endswith("metrics") or url_path.endswith("metrics/")):
        return

    # Dropping the children resets them, so the following `inc` leaves each
    # child at the number of registrations rather than accumulating scrapes.
    # Both counting functions share the metric, so this has to happen once,
    # before either of them runs.
    METRIC_REGISTRATION_COUNT.clear()

    async with (
        mora.db._get_sessionmaker(info.request)() as session,
        session.begin(),
    ):
        await org_func_registration_count(session)
        await object_registrations_count(session)


def setup_registration_metrics(instrumentator: Instrumentator) -> None:
    instrumentator.add(registration_count)
