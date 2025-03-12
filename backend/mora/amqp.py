# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""This file implements the event subsystem.

The purpose of this is to facilitate implementation and maintainability of
correct event-driven OS2MO integrations.

We guarantee at least one event every time there is a new registration, or a
validity range goes into or out of effect. Note that there could be multiple
events emitted even though there are no observable state changes, so make sure
any integration is idempotent.

The event is posted to a RabbitMQ topic exchange, where the routing key is the
object type (e.g. "org_unit") and the content is the UUID of the affected
object.
"""

# TODO: Do we wanna access-log database access from here?
import asyncio
import random
from typing import Literal
from uuid import UUID

from fastramqpi.ramqp import AMQPSystem
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import union
from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog import get_logger

from mora.config import get_settings
from mora.db import AMQPSubsystem
from mora.db import AsyncSession
from mora.db import BrugerAttrEgenskaber
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import BrugerTilsGyldighed
from mora.db import FacetAttrEgenskaber
from mora.db import FacetRegistrering
from mora.db import FacetRelation
from mora.db import FacetTilsPubliceret
from mora.db import ITSystemAttrEgenskaber
from mora.db import ITSystemRegistrering
from mora.db import ITSystemRelation
from mora.db import ITSystemTilsGyldighed
from mora.db import KlasseAttrEgenskaber
from mora.db import KlasseRegistrering
from mora.db import KlasseRelation
from mora.db import KlasseTilsPubliceret
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedRelation
from mora.db import OrganisationEnhedTilsGyldighed
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionTilsGyldighed

logger = get_logger()


MO_TYPE = Literal[
    "address",
    "association",
    "class",
    "engagement",
    "facet",
    "itsystem",
    "ituser",
    "kle",
    "leave",
    "manager",
    "manager",
    "org_unit",
    "owner",
    "person",
    "related_unit",
    "rolebinding",
]


_lora_to_mo: dict[str, MO_TYPE] = {
    "bruger": "person",
    "facet": "facet",
    "itsystem": "itsystem",
    "klasse": "class",
    "organisationenhed": "org_unit",
    # Funktionsnavne (see mora.db.FunktionsNavn)
    "Adresse": "address",
    "Engagement": "engagement",
    "IT-system": "ituser",
    "KLE": "kle",
    "Leder": "manager",
    "Orlov": "leave",
    "Relateret Enhed": "related_unit",
    "Rollebinding": "rolebinding",
    "Tilknytning": "association",
    "owner": "owner",
}


async def _send_amqp_message(
    amqp_system: AMQPSystem, object_type: MO_TYPE, uuid: UUID
) -> None:
    await amqp_system.publish_message(
        routing_key=object_type,
        payload=str(uuid),
    )


async def _emit_events(
    session: AsyncSession, amqp_system: AMQPSystem
) -> None:  # pragma: no cover
    """Send an event for every new registration or validity we've passed since last run."""
    logger.info("emitting amqp events")
    # We need to fetch "now" before our queries, or we expose ourself to
    # race-conditions when updating the table in the end.
    last_run = await session.scalar(
        select(AMQPSubsystem.last_run).where(AMQPSubsystem.id == 1)
    )
    now = await session.scalar(select(func.now()))

    def registration_condition(cls):
        return cls.registreringstid_start.between(last_run, now)

    def validity_condition(cls):
        return or_(
            cls.virkning_start.between(last_run, now),
            cls.virkning_slut.between(last_run, now),
        )

    query = union(
        select(text("'bruger'"), BrugerRegistrering.bruger_id)
        .distinct()
        .where(
            BrugerRegistrering.id.in_(
                union(
                    select(BrugerRegistrering.id).where(
                        registration_condition(BrugerRegistrering)
                    ),
                    select(BrugerAttrEgenskaber.bruger_registrering_id).where(
                        validity_condition(BrugerAttrEgenskaber)
                    ),
                    select(BrugerAttrUdvidelser.bruger_registrering_id).where(
                        validity_condition(BrugerAttrUdvidelser)
                    ),
                    select(BrugerTilsGyldighed.bruger_registrering_id).where(
                        validity_condition(BrugerTilsGyldighed)
                    ),
                    select(BrugerRelation.bruger_registrering_id).where(
                        validity_condition(BrugerRelation)
                    ),
                )
            )
        ),
        select(text("'facet'"), FacetRegistrering.facet_id)
        .distinct()
        .where(
            FacetRegistrering.id.in_(
                union(
                    select(FacetRegistrering.id).where(
                        registration_condition(FacetRegistrering)
                    ),
                    select(FacetAttrEgenskaber.facet_registrering_id).where(
                        validity_condition(FacetAttrEgenskaber)
                    ),
                    select(FacetTilsPubliceret.facet_registrering_id).where(
                        validity_condition(FacetTilsPubliceret)
                    ),
                    select(FacetRelation.facet_registrering_id).where(
                        validity_condition(FacetRelation)
                    ),
                )
            )
        ),
        select(text("'itsystem'"), ITSystemRegistrering.itsystem_id)
        .distinct()
        .where(
            ITSystemRegistrering.id.in_(
                union(
                    select(ITSystemRegistrering.id).where(
                        registration_condition(ITSystemRegistrering)
                    ),
                    select(ITSystemAttrEgenskaber.itsystem_registrering_id).where(
                        validity_condition(ITSystemAttrEgenskaber)
                    ),
                    select(ITSystemTilsGyldighed.itsystem_registrering_id).where(
                        validity_condition(ITSystemTilsGyldighed)
                    ),
                    select(ITSystemRelation.itsystem_registrering_id).where(
                        validity_condition(ITSystemRelation)
                    ),
                )
            )
        ),
        select(text("'klasse'"), KlasseRegistrering.klasse_id)
        .distinct()
        .where(
            KlasseRegistrering.id.in_(
                union(
                    select(KlasseRegistrering.id).where(
                        registration_condition(KlasseRegistrering)
                    ),
                    select(KlasseAttrEgenskaber.klasse_registrering_id).where(
                        validity_condition(KlasseAttrEgenskaber)
                    ),
                    select(KlasseTilsPubliceret.klasse_registrering_id).where(
                        validity_condition(KlasseTilsPubliceret)
                    ),
                    select(KlasseRelation.klasse_registrering_id).where(
                        validity_condition(KlasseRelation)
                    ),
                )
            )
        ),
        select(
            text("'organisationenhed'"),
            OrganisationEnhedRegistrering.organisationenhed_id,
        )
        .distinct()
        .where(
            OrganisationEnhedRegistrering.id.in_(
                union(
                    select(OrganisationEnhedRegistrering.id).where(
                        registration_condition(OrganisationEnhedRegistrering)
                    ),
                    select(
                        OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
                    ).where(validity_condition(OrganisationEnhedAttrEgenskaber)),
                    select(
                        OrganisationEnhedTilsGyldighed.organisationenhed_registrering_id
                    ).where(validity_condition(OrganisationEnhedTilsGyldighed)),
                    select(
                        OrganisationEnhedRelation.organisationenhed_registrering_id
                    ).where(validity_condition(OrganisationEnhedRelation)),
                )
            )
        ),
        select(
            # Notice we select "funktionsnavn" here. Used in `_lora_to_mo`.
            OrganisationFunktionAttrEgenskaber.funktionsnavn.cast(Text),
            OrganisationFunktionRegistrering.organisationfunktion_id,
        )
        .distinct()
        .join(
            OrganisationFunktionAttrEgenskaber,
            OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            == OrganisationFunktionRegistrering.id,
        )
        .where(
            OrganisationFunktionRegistrering.id.in_(
                union(
                    select(OrganisationFunktionRegistrering.id).where(
                        registration_condition(OrganisationFunktionRegistrering)
                    ),
                    select(
                        OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                    ).where(validity_condition(OrganisationFunktionAttrEgenskaber)),
                    select(
                        OrganisationFunktionTilsGyldighed.organisationfunktion_registrering_id
                    ).where(validity_condition(OrganisationFunktionTilsGyldighed)),
                    select(
                        OrganisationFunktionRelation.organisationfunktion_registrering_id
                    ).where(validity_condition(OrganisationFunktionRelation)),
                )
            ),
            OrganisationFunktionAttrEgenskaber.funktionsnavn.in_(_lora_to_mo.keys()),
        ),
    ).execution_options(yield_per=55)

    result = await session.stream(query)

    # https://docs.sqlalchemy.org/en/20/core/connections.html#using-server-side-cursors-a-k-a-stream-results
    # Client-side partitioning seems to cause 100% CPU usage constantly.

    async for rows in result.partitions():
        await asyncio.gather(
            *(
                _send_amqp_message(amqp_system, _lora_to_mo[lora_type], uuid)
                for lora_type, uuid in rows
            )
        )

    await session.execute(
        update(AMQPSubsystem),
        [
            {"id": 1, "last_run": now},
        ],
    )


async def start_amqp_subsystem(
    sessionmaker: async_sessionmaker,
) -> None:  # pragma: no cover
    mo_settings = get_settings()

    logger.info("starting amqp subsystem")

    amqp_system = AMQPSystem(mo_settings.amqp)
    async with amqp_system:
        while True:
            # Why sleep for a random duration? Otherwise, developers will build on
            # the assumption that events arrive instantly. Are you a developer
            # tired of waiting? See if the mora.cli can help you.
            await asyncio.sleep(random.randint(5, 90))
            try:
                async with sessionmaker() as session, session.begin():
                    await _emit_events(session, amqp_system)
            except:  # noqa
                logger.exception("failed to send events")
