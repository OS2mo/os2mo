# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.db import OrganisationFunktionTilsGyldighed


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
