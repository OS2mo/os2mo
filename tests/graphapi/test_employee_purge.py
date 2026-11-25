# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mora.db import Bruger
from mora.db import OrganisationFunktion
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db.events import Event
from mora.db.events import Listener
from mora.mapping import OWNER
from tests.conftest import AnotherTransaction
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied

PAST = {"from": "2000-01-01T00:00:00+01:00", "to": "2001-01-01T00:00:00+01:00"}
CURRENT = {"from": "2000-01-01T00:00:00+01:00", "to": None}
FUTURE = {"from": "2100-01-01T00:00:00+01:00", "to": None}
SUBSTITUTE_ASSOCIATION_TYPE = "6c4f9b0e-4a8e-4f4b-9d0a-2b3c8e5f1a7d"
SUBSTITUTE_ROLES = pytest.mark.envvar(
    {"CONFDB_SUBSTITUTE_ROLES": json.dumps([SUBSTITUTE_ASSOCIATION_TYPE])}
)


@pytest.fixture
def org_unit(create_org_unit: Callable[..., UUID]) -> UUID:
    return create_org_unit("unit")


@pytest.fixture
def address_type(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> UUID:
    facet = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "1970-01-01"}}
    )
    return create_class(
        {
            "user_key": "EmailEmployee",
            "name": "Email",
            "scope": "TEXT",
            "facet_uuid": str(facet),
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def itsystem(create_itsystem: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_itsystem(
        {"user_key": "ad", "name": "Active Directory", "validity": CURRENT}
    )


@pytest.fixture
def make_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID], org_unit: UUID
) -> Callable[[UUID, dict[str, Any]], UUID]:
    def inner(person: UUID, validity: dict[str, Any]) -> UUID:
        return create_engagement(
            {
                "person": str(person),
                "org_unit": str(org_unit),
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "validity": validity,
            }
        )

    return inner


@pytest.fixture
def make_ituser(
    create_ituser: Callable[[dict[str, Any]], UUID], itsystem: UUID
) -> Callable[[UUID, dict[str, Any]], UUID]:
    def inner(person: UUID, validity: dict[str, Any]) -> UUID:
        return create_ituser(
            {
                "user_key": str(uuid4()),
                "person": str(person),
                "itsystem": str(itsystem),
                "validity": validity,
            }
        )

    return inner


@pytest.fixture
def make_manager(graphapi_post: GraphAPIPost, org_unit: UUID) -> Callable[..., UUID]:
    def inner(
        person: UUID, validity: dict[str, Any], engagement: UUID | None = None
    ) -> UUID:
        response = graphapi_post(
            """
            mutation CreateManager($input: ManagerCreateInput!) {
                manager_create(input: $input) { uuid }
            }
            """,
            {
                "input": {
                    "person": str(person),
                    "engagement": str(engagement) if engagement else None,
                    "org_unit": str(org_unit),
                    "manager_type": str(uuid4()),
                    "manager_level": str(uuid4()),
                    "responsibility": [],
                    "validity": validity,
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_create"]["uuid"])

    return inner


@pytest.fixture
def make_substitute_association(
    create_association: Callable[[dict[str, Any]], UUID], org_unit: UUID
) -> Callable[[UUID, UUID, dict[str, Any]], UUID]:
    def inner(person: UUID, substitute: UUID, validity: dict[str, Any]) -> UUID:
        return create_association(
            {
                "person": str(person),
                "substitute": str(substitute),
                "org_unit": str(org_unit),
                "association_type": SUBSTITUTE_ASSOCIATION_TYPE,
                "validity": validity,
            }
        )

    return inner


@pytest.fixture
def purge(graphapi_post: GraphAPIPost) -> Callable[[UUID], GQLResponse]:
    def inner(person: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation PurgeEmployee($uuid: UUID!) {
                employee_purge(uuid: $uuid)
            }
            """,
            {"uuid": str(person)},
        )

    return inner


@pytest.fixture
def exists(empty_db: AsyncSession) -> Callable[[UUID], Awaitable[bool]]:
    """Whether a person or org function exists, in any registration."""

    async def inner(uuid: UUID) -> bool:
        for model in (Bruger, OrganisationFunktion):
            if await empty_db.scalar(select(model.id).where(model.id == uuid)):
                return True
        return False

    return inner


@pytest.fixture
def org_func_relations(empty_db: AsyncSession) -> Callable[[UUID], Awaitable[set]]:
    """What an org function points at, in any registration."""

    async def inner(uuid: UUID) -> set:
        return set(
            await empty_db.scalars(
                select(OrganisationFunktionRelation.rel_maal_uuid)
                .join(OrganisationFunktionRegistrering)
                .where(OrganisationFunktionRegistrering.organisationfunktion_id == uuid)
            )
        )

    return inner


def refused(response: GQLResponse) -> list[dict[str, str]]:
    """
    The org functions refusing the purge, as returned by the mutation.

    They are read from the error's `refused` field, after asserting that the
    purge was refused. Each org function is a dict with its UUID, its
    funktionsnavn and the reason it refuses the purge, sorted by UUID, e.g.:

        [
            {
                "uuid": "0e4ad1d4-9a35-4a2d-9b8e-2f0c3c5b7a11",
                "type": "Engagement",
                "reason": "refuse_active",
            },
            {
                "uuid": "7c1f9e2a-3b44-4d1e-8f2a-6a9d0e5b4c22",
                "type": "Adresse",
                "reason": "refuse_foreign",
            },
        ]
    """
    assert response.data is None
    assert response.errors is not None
    error_context = one(response.errors)["extensions"]["error_context"]
    assert error_context["error_key"] == "V_PURGE_EMPLOYEE_REFUSED"
    return error_context["refused"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_deletes_the_persons_own_org_functions(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_ituser: Callable[[UUID, dict[str, Any]], UUID],
    address_type: UUID,
    org_unit: UUID,
    create_address: Callable[[dict[str, Any]], UUID],
    create_association: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that the person and every org function of theirs are deleted.

    The person is given one org function of every kind which belongs to
    them alone, all of them in the past, so none of them refuses the purge:

    - an engagement, updated once, so it has two registrations
    - an IT user, and a role binding on it
    - an address, an association, and a leave from the engagement
    - an owner where somebody else owns the person, and one where the
      person owns somebody else

    Somebody else's current engagement is made too, to show that the purge
    leaves other people's data alone.
    """
    # Arrange
    person = create_person()
    other = create_person()
    engagement = make_engagement(person, PAST)
    # A second registration, which must be deleted too
    update_engagement(
        {"uuid": str(engagement), "user_key": "changed", "validity": PAST}
    )
    ituser = make_ituser(person, PAST)
    own = {
        engagement,
        ituser,
        create_rolebinding(
            {"ituser": str(ituser), "role": str(uuid4()), "validity": PAST}
        ),
        create_address(
            {
                "person": str(person),
                "address_type": str(address_type),
                "value": "spam@eggs.invalid",
                "validity": PAST,
            }
        ),
        create_association(
            {
                "person": str(person),
                "org_unit": str(org_unit),
                "association_type": str(uuid4()),
                "validity": PAST,
            }
        ),
        create_leave(
            {
                "person": str(person),
                "engagement": str(engagement),
                "leave_type": str(uuid4()),
                "validity": PAST,
            }
        ),
        # The person being owned, and owning somebody else
        create_owner({"owner": str(other), "person": str(person), "validity": PAST}),
        create_owner({"owner": str(person), "person": str(other), "validity": PAST}),
    }
    others_engagement = make_engagement(other, CURRENT)

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert response.data == {"employee_purge": str(person)}
    assert not await exists(person)
    for uuid in own:
        assert not await exists(uuid)
    assert await exists(other)
    assert await exists(others_engagement)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("validity", [CURRENT, FUTURE])
async def test_purge_is_refused_by_active_org_functions(
    validity: dict[str, Any],
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that an org function active now or in the future refuses the purge.

    The person is given two engagements: one in the past, which alone would
    be deleted, and one which is active now or starts in the future. Only the
    active one refuses the purge, and the past one is still there afterwards,
    as nothing is deleted when the purge is refused.
    """
    # Arrange
    person = create_person()
    past_engagement = make_engagement(person, PAST)
    active_engagement = make_engagement(person, validity)

    # Act
    response = purge(person)

    # Assert
    assert refused(response) == [
        {
            "uuid": str(active_engagement),
            "type": "Engagement",
            "reason": "refuse_active",
        }
    ]
    assert await exists(person)
    assert await exists(past_engagement)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_is_refused_by_foreign_org_functions(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_ituser: Callable[[UUID, dict[str, Any]], UUID],
    address_type: UUID,
    org_unit: UUID,
    create_address: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    update_ituser: Callable[[dict[str, Any]], UUID],
    update_rolebinding: Callable[[dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    The scenarios in this test are very very edge cases, but they are possible in MO why
    we should test them.

    Test that org functions not belonging to the person alone refuse the purge.

    The person is given a past engagement and IT user, which alone would be
    deleted, and three org functions which also belong to somebody else:

    - an org unit's address, tied to the person's engagement
    - an IT user, moved from the person to somebody else in a later
      registration
    - a role binding, moved from the person's IT user to somebody else's

    All of them are in the past, so they refuse the purge for not being the
    person's own, rather than for being active.
    """
    # Arrange
    person = create_person()
    other = create_person()
    engagement = make_engagement(person, PAST)
    ituser = make_ituser(person, PAST)
    # An org unit's address, tied to the person's engagement
    org_unit_address = create_address(
        {
            "org_unit": str(org_unit),
            "engagement": str(engagement),
            "address_type": str(address_type),
            "value": "spam@eggs.invalid",
            "validity": PAST,
        }
    )
    # An IT user moved from the person to somebody else
    moved_ituser = make_ituser(person, PAST)
    update_ituser({"uuid": str(moved_ituser), "person": str(other), "validity": PAST})
    # A role binding moved from the person's IT user to somebody else's
    rolebinding = create_rolebinding(
        {"ituser": str(ituser), "role": str(uuid4()), "validity": PAST}
    )
    update_rolebinding(
        {
            "uuid": str(rolebinding),
            "ituser": str(make_ituser(other, PAST)),
            "validity": PAST,
        },
    )

    # Act
    response = purge(person)

    # Assert
    assert sorted(refused(response), key=lambda r: r["uuid"]) == sorted(
        [
            {
                "uuid": str(org_unit_address),
                "type": "Adresse",
                "reason": "refuse_foreign",
            },
            {
                "uuid": str(moved_ituser),
                "type": "IT-system",
                "reason": "refuse_foreign",
            },
            {
                "uuid": str(rolebinding),
                "type": "Rollebinding",
                "reason": "refuse_foreign",
            },
        ],
        key=lambda r: r["uuid"],
    )
    assert await exists(person)
    assert await exists(engagement)
    assert await exists(ituser)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_vacates_manager_roles(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_manager: Callable[..., UUID],
    org_unit: UUID,
    update_manager: Callable[[UUID, UUID | None], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
    org_func_relations: Callable[[UUID], Awaitable[set]],
) -> None:
    """
    Test that manager roles are kept, with the person removed from them.

    The person is given two manager roles:

    - one held through their past engagement, also in the past, which loses
      both the person and the engagement
    - one moved from the person to somebody else, who holds it now, which
      loses only the person

    Both still point at their org unit, and the moved one at its new holder.
    """
    # Arrange
    person = create_person()
    other = create_person()
    engagement = make_engagement(person, PAST)
    # Held by the person through their engagement, in the past
    past_manager = make_manager(person, PAST, engagement)
    # Moved from the person to somebody else, who holds it now
    moved_manager = make_manager(person, CURRENT)
    update_manager(moved_manager, other)

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert not await exists(engagement)
    assert await exists(past_manager)
    assert await exists(moved_manager)
    past_relations = await org_func_relations(past_manager)
    assert not past_relations & {person, engagement}
    assert org_unit in past_relations

    moved_relations = await org_func_relations(moved_manager)
    assert person not in moved_relations
    assert {other, org_unit} <= moved_relations


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("validity", [CURRENT, FUTURE])
async def test_purge_is_refused_by_manager_roles_held_by_the_person(
    validity: dict[str, Any],
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_manager: Callable[..., UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that a manager role held now or in the future refuses the purge.

    Unlike a past manager role, which is made vacant, a manager role the
    person holds now or from a future date refuses the purge.
    """
    # Arrange
    person = create_person()
    manager = make_manager(person, validity)

    # Act
    response = purge(person)

    # Assert
    assert refused(response) == [
        {"uuid": str(manager), "type": "Leder", "reason": "refuse_active"}
    ]
    assert await exists(person)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_keeps_explicit_managers_of_other_engagements(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_manager: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
    org_func_relations: Callable[[UUID], Awaitable[set]],
) -> None:
    """
    Test that an engagement with the person's manager role as explicit manager
    does not refuse the purge.

    The person is given a past manager role, which somebody else's current
    engagement has as its explicit manager. The engagement points at the
    manager role, not at the person, and the manager role is made vacant
    rather than deleted, so the engagement keeps pointing at it.
    """
    # Arrange
    person = create_person()
    other = create_person()
    manager = make_manager(person, PAST)
    others_engagement = make_engagement(other, CURRENT)
    update_engagement(
        {
            "uuid": str(others_engagement),
            "explicit_manager": str(manager),
            "validity": CURRENT,
        }
    )

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert not await exists(person)
    assert await exists(manager)
    assert person not in await org_func_relations(manager)
    assert await exists(others_engagement)
    assert manager in await org_func_relations(others_engagement)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_deletes_engagements_with_an_explicit_manager(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_manager: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
    org_func_relations: Callable[[UUID], Awaitable[set]],
) -> None:
    """
    Test that the person's engagement is deleted, and its explicit manager kept.

    The person is given a past engagement, with somebody else's current
    manager role as its explicit manager. The engagement is deleted like any
    other of the person's, and the manager role, which does not point at the
    engagement, is left alone.
    """
    # Arrange
    person = create_person()
    other = create_person()
    others_manager = make_manager(other, CURRENT)
    engagement = make_engagement(person, PAST)
    update_engagement(
        {
            "uuid": str(engagement),
            "explicit_manager": str(others_manager),
            "validity": PAST,
        }
    )

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert not await exists(person)
    assert not await exists(engagement)
    assert await exists(others_manager)
    assert other in await org_func_relations(others_manager)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@SUBSTITUTE_ROLES
async def test_purge_vacates_substitute_associations(
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_substitute_association: Callable[[UUID, UUID, dict[str, Any]], UUID],
    org_unit: UUID,
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
    org_func_relations: Callable[[UUID], Awaitable[set]],
) -> None:
    """
    Test that associations are kept, with the person removed as substitute.

    Somebody else is given a past association with the person as their
    substitute. The association still points at its own person and org
    unit afterwards, but no longer at the purged person.
    """
    # Arrange
    person = create_person()
    other = create_person()
    association = make_substitute_association(other, person, PAST)

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert not await exists(person)
    assert await exists(association)
    relations = await org_func_relations(association)
    assert person not in relations
    assert {other, org_unit} <= relations


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@SUBSTITUTE_ROLES
@pytest.mark.parametrize("validity", [CURRENT, FUTURE])
async def test_purge_is_refused_by_active_substitutions(
    validity: dict[str, Any],
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_substitute_association: Callable[[UUID, UUID, dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that being a substitute now or in the future refuses the purge.

    Somebody else is given an association, active now or from a future date,
    with the person as their substitute. Unlike a past one, which is made
    vacant, it refuses the purge.
    """
    # Arrange
    person = create_person()
    other = create_person()
    association = make_substitute_association(other, person, validity)

    # Act
    response = purge(person)

    # Assert
    assert refused(response) == [
        {"uuid": str(association), "type": "Tilknytning", "reason": "refuse_active"}
    ]
    assert await exists(person)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_sends_events(
    empty_db: AsyncSession,
    another_transaction: AnotherTransaction,
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    make_manager: Callable[..., UUID],
    purge: Callable[[UUID], GQLResponse],
) -> None:
    """
    Test that the purge sends an event for everything it changes, and only then.

    Two people are purged:

    - one with a past engagement, and a past manager role held through it,
      which is purged
    - one with a current engagement, which refuses the purge

    Listeners for persons, engagements and manager roles only get events for
    the first: the person, their deleted engagement and their vacated manager
    role.
    """
    # Arrange
    purged = create_person()
    refused_person = create_person()
    engagement = make_engagement(purged, PAST)
    manager = make_manager(purged, PAST, engagement)
    make_engagement(refused_person, CURRENT)
    # A request opens its own session, so the listeners must be committed to it
    async with another_transaction() as (_, session):
        listeners = {
            routing_key: Listener(
                user_key=routing_key,
                owner=uuid4(),
                routing_key=routing_key,
                namespace_fk="mo",
            )
            for routing_key in ("person", "engagement", "manager")
        }
        session.add_all(listeners.values())
        await session.flush()
        listener_uuids = {
            routing_key: listener.pk for routing_key, listener in listeners.items()
        }

    # Act
    purge(refused_person)
    purge(purged)

    # Assert
    async def subjects(routing_key: str) -> set[str]:
        return set(
            await empty_db.scalars(
                select(Event.subject).where(
                    Event.listener_fk == listener_uuids[routing_key]
                )
            )
        )

    assert await subjects("person") == {str(purged)}
    assert await subjects("engagement") == {str(engagement)}
    assert await subjects("manager") == {str(manager)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_deletes_org_functions_with_legacy_function_names(
    another_transaction: AnotherTransaction,
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_engagement: Callable[[UUID, dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that org functions with a funktionsnavn outside the enum are purged.

    The person is given a past engagement, which is then changed directly in
    the database to the funktionsnavn "Rolle", as found in old databases. It
    is deleted like any other org function of the person's.
    """
    # Arrange
    person = create_person()
    legacy_engagement = make_engagement(person, PAST)
    # Old databases hold kinds of org functions MO no longer knows, e.g. "Rolle"
    async with another_transaction() as (_, session):
        await session.execute(
            text(
                "UPDATE organisationfunktion_attr_egenskaber"
                " SET funktionsnavn = 'Rolle'"
                " WHERE organisationfunktion_registrering_id IN ("
                " SELECT id FROM organisationfunktion_registrering"
                " WHERE organisationfunktion_id = :uuid)"
            ),
            {"uuid": legacy_engagement},
        )

    # Act
    response = purge(person)

    # Assert
    assert response.errors is None
    assert not await exists(person)
    assert not await exists(legacy_engagement)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_purge_of_unknown_person(purge: Callable[[UUID], GQLResponse]) -> None:
    """
    Test that purging an unknown person fails.

    Nothing is arranged: the UUID belongs to nobody, so the purge fails with
    E_USER_NOT_FOUND.
    """
    # Act
    response = purge(uuid4())

    # Assert
    assert response.errors is not None
    error_context = one(response.errors)["extensions"]["error_context"]
    assert error_context["error_key"] == "E_USER_NOT_FOUND"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_purge_is_denied_to_the_owner(
    set_auth: SetAuth,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    purge: Callable[[UUID], GQLResponse],
    exists: Callable[[UUID], Awaitable[bool]],
) -> None:
    """
    Test that owning a person does not allow purging them.

    Somebody is made the owner of the person, and calls the mutation with
    only the owner role. Owning a person allows editing them, but the purge
    requires the admin role or a write rule granting it, so it is denied, and
    the person is still there afterwards.
    """
    # Arrange
    owner = create_person()
    person = create_person()
    create_owner({"owner": str(owner), "person": str(person), "validity": CURRENT})
    set_auth(OWNER, owner)

    # Act
    response = purge(person)

    # Assert
    assert_denied(response)
    assert await exists(person)
