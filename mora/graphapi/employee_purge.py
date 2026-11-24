# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from enum import StrEnum
from enum import auto
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Text
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import type_coerce
from sqlalchemy.ext.asyncio import AsyncSession

from mora import exceptions
from mora.db import Bruger
from mora.db import BrugerAttrEgenskaber
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import BrugerTilsGyldighed
from mora.db import OrganisationFunktion
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionAttrUdvidelser
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


class PurgeDecision(StrEnum):
    """What the purge does with an org function."""

    # Delete the org function, in all its registrations
    DELETE = auto()
    # Keep the manager role, but remove the person from it
    VACATE = auto()
    # Refuse the purge, as the org function is active now or in the future
    REFUSE_ACTIVE = auto()
    # Refuse the purge, as the org function is not the person's own
    REFUSE_FOREIGN = auto()


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


def find_own_org_functions(
    person: UUID, org_function_data: dict[UUID, OrgFunctionData]
) -> set[UUID]:
    """
    Find the org functions which belong to the person, and only ever did.

    An org function is the person's own when:

    - Engagement, IT user, address, association, leave and any other kind:
      the person is the only employee it has ever had
      (tilknyttedebrugere == {person}).
    - Manager role: not decided here, as manager roles are made vacant.
    - Role binding: it is tied to at least one IT user, and every IT user it
      has been tied to (tilknyttedefunktioner) is the person's own.
    - Owner: the person is the only owned person it has ever had
      (tilknyttedebrugere == {person}), or the only owner
      (tilknyttedepersoner == {person}).

    Comparing with {person}, rather than checking for the person, is what
    makes it "only ever": an IT user moved from the person to somebody else
    has both in tilknyttedebrugere, and is not the person's own.

    Args:
        person: UUID of the person.
        org_function_data: The data of the org functions to decide on, keyed
            by their UUIDs.

    Returns:
        UUIDs of the person's own org functions among those given.
    """
    only_person = {person}
    own: set[UUID] = set()
    for uuid, org_function in org_function_data.items():
        if org_function.funktionsnavn in ("Leder", "Rollebinding"):
            continue
        if org_function.tilknyttedebrugere == only_person or (
            org_function.funktionsnavn == "owner"
            and org_function.tilknyttedepersoner == only_person
        ):
            own.add(uuid)

    # Role bindings go last, as they depend on the IT users found above
    own_role_bindings = {
        uuid
        for uuid, org_function in org_function_data.items()
        if org_function.funktionsnavn == "Rollebinding"
        and org_function.tilknyttedefunktioner
        and org_function.tilknyttedefunktioner <= own
    }

    return own | own_role_bindings


async def find_active_manager_roles_held_by_person(
    session: AsyncSession, person: UUID, uuids: set[UUID]
) -> set[UUID]:
    """
    Find the manager roles which the person holds now or in the future.

    Args:
        session: The database session to query in.
        person: UUID of the person.
        uuids: UUIDs of the manager roles to check.

    Returns:
        UUIDs of the manager roles held by the person among those given.
    """
    result = await session.scalars(
        select(OrganisationFunktionRegistrering.organisationfunktion_id)
        .distinct()
        .join(OrganisationFunktionRelation)
        .where(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids),
            OrganisationFunktionRegistrering.registrering_period.contains(func.now()),
            OrganisationFunktionRegistrering.lifecycle != "Slettet",
            OrganisationFunktionRelation.rel_type
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            OrganisationFunktionRelation.rel_maal_uuid == person,
            # Held, and the manager role active, at some point from now on
            OrganisationFunktionRelation.aktiv_virkning.overlaps(
                func.tstzrange(func.now(), None)
            ),
        )
    )
    return set(result)


def decide_purge(
    org_function_data: dict[UUID, OrgFunctionData],
    own: set[UUID],
    active: set[UUID],
    active_manager_roles_held_by_person: set[UUID],
) -> dict[UUID, PurgeDecision]:
    """
    Decide what the purge does with each org function.

    Args:
        org_function_data: The data of the org functions to decide on, keyed
            by their UUIDs.
        own: UUIDs of the person's own org functions.
        active: UUIDs of the org functions active now or in the future.
        active_manager_roles_held_by_person: UUIDs of the manager roles the
            person holds now or in the future.

    Returns:
        The decision on each org function, keyed by their UUIDs.
    """
    decisions: dict[UUID, PurgeDecision] = dict()
    for uuid, org_function in org_function_data.items():
        is_manager_role = org_function.funktionsnavn == "Leder"

        # The checks are made in order, and the first one to match decides.

        # 1. A manager role the person holds now or in the future
        if is_manager_role and uuid in active_manager_roles_held_by_person:
            decision = PurgeDecision.REFUSE_ACTIVE

        # 2. Any other manager role. Manager roles are checked before
        #    ownership (since find_own_org_functions leaves them out), as they
        #    would otherwise all be refused as foreign in 3.
        elif is_manager_role:
            decision = PurgeDecision.VACATE

        # 3. Not the person's own. Checked before activity, as such an org
        #    function is refused whether active or not, and the decision should
        #    tell the caller that it is not the person's, rather than that it
        #    is active.
        elif uuid not in own:
            decision = PurgeDecision.REFUSE_FOREIGN

        # 4. One of the person's own, active now or in the future
        elif uuid in active:
            decision = PurgeDecision.REFUSE_ACTIVE

        # 5. Everything else
        else:
            decision = PurgeDecision.DELETE

        decisions[uuid] = decision

    return decisions


async def delete_org_functions(session: AsyncSession, uuids: set[UUID]) -> None:
    """
    Delete org functions, in all their registrations.

    The rows are deleted directly in the database, bypassing the bitemporal
    history, so the org functions disappear as if they had never existed.

    The transaction is not committed, so the deletion can be part of a larger
    one.

    Args:
        session: The database session to delete in.
        uuids: UUIDs of the org functions to delete.
    """
    registrations = select(OrganisationFunktionRegistrering.id).where(
        OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids)
    )
    # The foreign keys do not cascade, so the rows must be deleted from the
    # leaves up. The validity rows go after the relation and attribute rows,
    # as a trigger on them updates those rows on every change.
    for table in (
        OrganisationFunktionRelation,
        OrganisationFunktionAttrEgenskaber,
        OrganisationFunktionAttrUdvidelser,
        OrganisationFunktionTilsGyldighed,
    ):
        await session.execute(
            delete(table).where(
                table.organisationfunktion_registrering_id.in_(registrations)
            )
        )
    await session.execute(
        delete(OrganisationFunktionRegistrering).where(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids)
        )
    )
    await session.execute(
        delete(OrganisationFunktion).where(OrganisationFunktion.id.in_(uuids))
    )


async def vacate_manager_roles(
    session: AsyncSession, uuids: set[UUID], removed: set[UUID]
) -> None:
    """
    Remove the purged person and their engagements from manager roles.

    A manager role points at the person holding it, and at the engagement
    they hold it through. Both are removed, in every registration, so the
    manager role does not point at anything deleted.

    The transaction is not committed, so the vacating can be part of a larger
    one.

    Args:
        session: The database session to delete in.
        uuids: UUIDs of the manager roles to vacate.
        removed: UUIDs of what is purged: the person and the deleted org
            functions. A manager role may point at both, as it is held by the
            person through one of their engagements.
    """
    registrations = select(OrganisationFunktionRegistrering.id).where(
        OrganisationFunktionRegistrering.organisationfunktion_id.in_(uuids)
    )
    await session.execute(
        delete(OrganisationFunktionRelation).where(
            OrganisationFunktionRelation.organisationfunktion_registrering_id.in_(
                registrations
            ),
            OrganisationFunktionRelation.rel_maal_uuid.in_(removed),
        )
    )


async def delete_person(session: AsyncSession, person: UUID) -> None:
    """
    Delete a person, in all their registrations.

    The transaction is not committed, so the deletion can be part of a larger
    one.

    Args:
        session: The database session to delete in.
        person: UUID of the person.
    """
    registrations = select(BrugerRegistrering.id).where(
        BrugerRegistrering.bruger_id == person
    )
    # The foreign keys do not cascade, so the rows must be deleted from the
    # leaves up. The validity rows go after the relation and attribute rows,
    # as a trigger on them updates those rows on every change.
    for table in (
        BrugerRelation,
        BrugerAttrEgenskaber,
        BrugerAttrUdvidelser,
        BrugerTilsGyldighed,
    ):
        await session.execute(
            delete(table).where(table.bruger_registrering_id.in_(registrations))
        )
    await session.execute(
        delete(BrugerRegistrering).where(BrugerRegistrering.bruger_id == person)
    )
    await session.execute(delete(Bruger).where(Bruger.id == person))


async def purge_employee(session: AsyncSession, person: UUID) -> None:
    """
    Purge a person and every org function belonging to them.

    The person and their org functions are deleted in all registrations, and
    removed from the manager roles they have held. Nothing is deleted if any
    related org function is refused, i.e. is active now or in the future, or
    does not belong to the person alone.

    The transaction is not committed, so the purge can be part of a larger
    one.

    Args:
        session: The database session to purge in.
        person: UUID of the person.

    Raises:
        HTTPException: E_USER_NOT_FOUND if the person does not exist, or
            V_PURGE_EMPLOYEE_REFUSED, listing the refused org functions, if
            any are refused.
    """
    if await session.scalar(select(Bruger.id).where(Bruger.id == person)) is None:
        exceptions.ErrorCodes.E_USER_NOT_FOUND(employee_uuid=person)

    related = await find_related_org_functions(session, person)
    org_function_data = await fetch_org_function_data(session, related)
    manager_roles = {
        uuid
        for uuid, org_function in org_function_data.items()
        if org_function.funktionsnavn == "Leder"
    }
    decisions = decide_purge(
        org_function_data,
        own=find_own_org_functions(person, org_function_data),
        active=await find_active_org_functions(session, related),
        active_manager_roles_held_by_person=(
            await find_active_manager_roles_held_by_person(
                session, person, manager_roles
            )
        ),
    )

    refused = [
        {
            "uuid": uuid,
            "type": org_function_data[uuid].funktionsnavn,
            "reason": decision,
        }
        for uuid, decision in sorted(decisions.items())
        if decision in (PurgeDecision.REFUSE_ACTIVE, PurgeDecision.REFUSE_FOREIGN)
    ]
    if refused:
        exceptions.ErrorCodes.V_PURGE_EMPLOYEE_REFUSED(refused=refused)

    deleted = {
        uuid for uuid, decision in decisions.items() if decision == PurgeDecision.DELETE
    }
    vacated = {
        uuid for uuid, decision in decisions.items() if decision == PurgeDecision.VACATE
    }
    await delete_org_functions(session, deleted)
    await vacate_manager_roles(session, vacated, removed={person} | deleted)
    await delete_person(session, person)
