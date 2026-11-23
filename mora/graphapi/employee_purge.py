# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import type_coerce
from sqlalchemy.ext.asyncio import AsyncSession

from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.db import OrganisationFunktionTilsGyldighed


class OrgFunctionData(BaseModel):
    """
    What an org function has pointed at, across all its registrations.

    Attributes:
        funktionsnavn: The kind of org function, e.g. "Engagement" or "owner".
        tilknyttedebrugere: The employees (on an owner: the owned persons).
        tilknyttedepersoner: The owners of an owner.
        tilknyttedefunktioner: What it is tied to, e.g.:
            - the engagement of a leave
            - the IT user of a role binding
            - the substitutes of an association
    """

    class Config:
        frozen = True

    funktionsnavn: str
    tilknyttedebrugere: set[UUID] = set()
    tilknyttedepersoner: set[UUID] = set()
    tilknyttedefunktioner: set[UUID] = set()


async def find_related_org_functions(session: AsyncSession, person: UUID) -> set[UUID]:
    """
    Find every organisationfunktion related directly or indirectly to a person.

    An org function is related if it points at the person, or at an org
    function already found, in any of its registrations. Org functions which
    turn out not to be the person's own, such as an org unit's address tied to
    their engagement, are found too.

    Args:
        session: The database session to query in.
        person: UUID of the person.

    Returns:
        UUIDs of the related organisationfunktioner.
    """
    directly_related = (
        select(OrganisationFunktionRegistrering.organisationfunktion_id)
        .join(OrganisationFunktionRelation)
        .where(
            OrganisationFunktionRelation.rel_maal_uuid == person,
            OrganisationFunktionRelation.rel_type.in_(
                [
                    # The person is the employee (on an owner: the owned
                    # person)
                    OrganisationFunktionRelationKode.tilknyttedebrugere,
                    # The person is the owner of an owner
                    OrganisationFunktionRelationKode.tilknyttedepersoner,
                    # The person is an association's substitute
                    OrganisationFunktionRelationKode.tilknyttedefunktioner,
                ]
            ),
        )
        .cte(recursive=True)
    )
    indirectly_related = (
        select(OrganisationFunktionRegistrering.organisationfunktion_id)
        .join(OrganisationFunktionRelation)
        # Within the recursion, directly_related holds the rows found in the
        # previous step, so org functions several steps away are found too
        .join(
            directly_related,
            OrganisationFunktionRelation.rel_maal_uuid
            == directly_related.c.organisationfunktion_id,
        )
        .where(
            OrganisationFunktionRelation.rel_type.in_(
                [
                    # The engagement / IT user an org function is tied to
                    OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    # The IT user of an association
                    OrganisationFunktionRelationKode.tilknyttedeitsystemer,
                ]
            )
        )
    )
    # UNION, not UNION ALL, drops org functions already found, which also ends
    # the recursion once a step finds nothing new
    related = directly_related.union(indirectly_related)

    result = await session.scalars(select(related.c.organisationfunktion_id))
    return set(result)


async def find_active_org_functions(
    session: AsyncSession, uuids: set[UUID]
) -> set[UUID]:
    """
    Find the org functions which are active now or in the future.

    Args:
        session: The database session to query in.
        uuids: UUIDs of the org functions to check.

    Returns:
        UUIDs of the active org functions among those given.
    """
    result = await session.scalars(
        select(OrganisationFunktionRegistrering.organisationfunktion_id)
        .distinct()
        .join(OrganisationFunktionTilsGyldighed)
        .where(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids),
            OrganisationFunktionRegistrering.registrering_period.contains(func.now()),
            OrganisationFunktionRegistrering.lifecycle != "Slettet",
            OrganisationFunktionTilsGyldighed.is_active(),
            # Active at some point from now on
            OrganisationFunktionTilsGyldighed.virkning_period.overlaps(
                func.tstzrange(func.now(), None)
            ),
        )
    )
    return set(result)


async def fetch_org_function_data(
    session: AsyncSession, uuids: set[UUID]
) -> dict[UUID, OrgFunctionData]:
    """
    Fetch the org function data deciding what a purge does with each org function.

    Args:
        session: The database session to query in.
        uuids: UUIDs of the org functions to fetch the data of.

    Returns:
        The data of each org function among those given.
    """
    function_names = await session.execute(
        select(
            OrganisationFunktionRegistrering.organisationfunktion_id,
            # funktionsnavn is mapped as an enum, but the column is really
            # just text, and old databases hold values outside the enum, e.g.
            # "Rolle". Read as text, so such org functions are purged too.
            type_coerce(OrganisationFunktionAttrEgenskaber.funktionsnavn, Text),
        )
        # An org function keeps its funktionsnavn in every registration
        .distinct()
        .join(OrganisationFunktionAttrEgenskaber)
        .where(OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids))
    )
    relations = await session.execute(
        select(
            OrganisationFunktionRegistrering.organisationfunktion_id,
            OrganisationFunktionRelation.rel_type,
            OrganisationFunktionRelation.rel_maal_uuid,
        )
        .distinct()
        .join(OrganisationFunktionRelation)
        .where(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids),
            OrganisationFunktionRelation.rel_type.in_(
                [
                    OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelationKode.tilknyttedepersoner,
                    OrganisationFunktionRelationKode.tilknyttedefunktioner,
                ]
            ),
            # Relations to a URN, rather than a UUID, are not used here
            OrganisationFunktionRelation.rel_maal_uuid.is_not(None),
        )
    )

    org_function_data = {
        uuid: OrgFunctionData(funktionsnavn=function_name)
        for uuid, function_name in function_names
    }
    for uuid, rel_type, rel_maal_uuid in relations:
        getattr(org_function_data[uuid], rel_type).add(rel_maal_uuid)

    return org_function_data
