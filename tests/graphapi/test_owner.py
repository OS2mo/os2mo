# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of what an owner may touch over GraphQL."""

from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_org_unit_object_and_hierarchy(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Alice owns `owned` directly and `root` (an ancestor of `child`)
    owned = create_org_unit("owned")
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    unowned = create_org_unit("unowned")
    make_owner(alice, org_unit=owned)
    make_owner(alice, org_unit=root)

    def edit(unit: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": unit,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A rename (no `parent`) exercises the _unit(i.uuid) rule without a move
    # A stranger owns nothing -> denied for both the unit and the descendant
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(owned, name="Renamed"))
    assert_denied(edit(child, name="Renamed"))
    assert_denied(edit(unowned, name="Renamed"))

    # Alice owns the descendant via its ancestor `root`, and `owned` directly
    set_auth(role="owner", user_uuid=alice)
    assert_granted(edit(child, name="Renamed"))
    assert_granted(edit(owned, name="Renamed"))
    # Alice cannot rename `unowned`, because she does not own it
    assert_denied(edit(unowned, name="Renamed"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_person_linked_detail(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An IT-user links only a person, so `_via_person` grants its owner
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, person=bob)

    def ituser_for(person: UUID) -> UUID:
        return create_ituser(
            {
                "user_key": str(person),
                "itsystem": str(itsystem),
                "person": str(person),
                "validity": {"from": "2020-01-01"},
            }
        )

    bobs = ituser_for(bob)
    carols = ituser_for(carol)

    def rename(ituser: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateITUser($input: ITUserUpdateInput!) {
                ituser_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": ituser,
                        "user_key": "changed",
                        "validity": {"from": "2020-01-01"},
                    }
                }
            ),
        )

    # A stranger owns nobody
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(rename(bobs))
    assert_denied(rename(carols))

    # Alice owns Bob, and only Bob
    set_auth(role="owner", user_uuid=alice)
    assert_granted(rename(bobs))
    assert_denied(rename(carols))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_employee_object_and_create(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, person=bob)

    def create() -> GQLResponse:
        return graphapi_post(
            """
            mutation CreatePerson($input: EmployeeCreateInput!) {
                employee_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"given_name": "New", "surname": "Comer"}}
            ),
        )

    # A stranger owns nobody, and a brand-new employee has no owners either
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(employee_update(bob))
    assert_denied(employee_update(carol))
    assert_denied(create())

    # Alice owns Bob, and only Bob
    set_auth(role="owner", user_uuid=alice)
    assert_granted(employee_update(bob))
    assert_denied(employee_update(carol))
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_create_under_owned_parent(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    owned = create_org_unit("owned")
    unowned = create_org_unit("unowned")
    make_owner(alice, org_unit=owned)

    def create(name: str, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateOU($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "name": name,
                        "user_key": name,
                        "org_unit_type": str(uuid4()),
                        "validity": {"from": "2020-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns no parent to create under
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create("theirs", parent=owned))
    assert_denied(create("theirs2", parent=unowned))
    assert_denied(create("theirsroot", parent=None))
    assert_denied(create("theirsnoparent"))

    set_auth(role="owner", user_uuid=alice)
    # Under an owned parent -> granted
    assert_granted(create("sub", parent=owned))
    # Under a parent Alice does not own -> denied
    assert_denied(create("sub2", parent=unowned))
    # A root unit (explicit null parent) has no parent to own -> denied
    assert_denied(create("newroot", parent=None))
    # An absent `parent` reaches the rule as no field at all -> denied
    assert_denied(create("noparent"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_move_requires_new_parent_ownership(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Alice owns `home` (and thus its descendant `movable`) and the `new_parent`,
    # but not `other`
    home = create_org_unit("home")
    movable = create_org_unit("movable", home)
    new_parent = create_org_unit("new-parent")
    other = create_org_unit("other")
    make_owner(alice, org_unit=home)
    make_owner(alice, org_unit=new_parent)

    def edit(unit: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": unit,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns neither the unit nor either parent
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(movable, parent=other))
    assert_denied(edit(movable, parent=new_parent))

    # Moving to a parent Alice does not own is denied: she owns the unit only
    set_auth(role="owner", user_uuid=alice)
    assert_denied(edit(movable, parent=other))
    # Moving to an owned new parent is granted
    assert_granted(edit(movable, parent=new_parent))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_create_naming_neither_unit_nor_person(
    set_auth: SetAuth,
    alice: UUID,
    graphapi_post: GraphAPIPost,
) -> None:
    # A facet links no org-unit or person, thus it cannot be owned
    def create(user_key: str) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateFacet($input: FacetCreateInput!) {
                facet_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"user_key": user_key, "validity": {"from": "2020-01-01"}}}
            ),
        )

    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create("theirs"))

    set_auth(role="owner", user_uuid=alice)
    assert_denied(create("hers"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_may_repeat_the_parent_it_already_has(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Repeating the parent an update already has is not a move
    top = create_org_unit("top")
    unit = create_org_unit("unit", top)
    grandchild = create_org_unit("grandchild", unit)
    make_owner(alice, org_unit=unit)

    def edit(unit: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": unit,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # Repeating the parent is no licence to edit: a stranger owns nothing
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(unit, name="Renamed", parent=top))
    assert_denied(edit(grandchild, name="Renamed", parent=unit))
    assert_denied(edit(unit, name="Renamed", parent=None))

    # Alice owns `unit`, and nothing above or below it
    set_auth(role="owner", user_uuid=alice)
    # Repeating the parent it already has -> granted, though she owns no ancestor
    assert_granted(edit(unit, name="Renamed", parent=top))
    # Owning the parent is enough on its own: `grandchild` may repeat the parent
    # Alice owns, even though she owns neither it nor `top` above it
    assert_granted(edit(grandchild, name="Renamed", parent=unit))
    # A move to the root names no parent to own, so the unit alone decides
    assert_granted(edit(unit, name="Renamed", parent=None))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_requires_all_items_owned(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    itsystem: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # itusers_create takes a list; the owner must own every item's person
    owned = create_person({"given_name": "Owned", "surname": "Person"})
    foreign = create_person({"given_name": "Foreign", "surname": "Person"})
    make_owner(alice, person=bob)
    make_owner(alice, person=owned)

    def create(*people: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateITUsers($input: [ITUserCreateInput!]!) {
                itusers_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {
                            "user_key": str(person),
                            "itsystem": itsystem,
                            "person": person,
                            "validity": {"from": "2020-01-01"},
                        }
                        for person in people
                    ]
                }
            ),
        )

    # A stranger owns nobody in the batch
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(bob, owned))
    assert_denied(create(bob, foreign))
    assert_denied(create())

    set_auth(role="owner", user_uuid=alice)
    # Every person in the batch is owned -> granted
    assert_granted(create(bob, owned))
    # One person is not owned -> the whole batch is denied
    assert_denied(create(bob, foreign))
    # An empty batch yields no check-specs, so it is denied rather than
    # vacuously granted
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_unit_linked_detail_and_hierarchy(
    create_org_unit: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A manager sits on an org-unit, and Alice owns only its ancestor
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    make_owner(alice, org_unit=(root))
    manager = create_manager(child)

    def edit(**fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateManager($input: ManagerUpdateInput!) {
                manager_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": manager,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns nothing -> denied
    def terminate() -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateManager($input: ManagerTerminateInput!) {
                manager_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"uuid": manager, "to": "2050-01-01"}}
            ),
        )

    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit())
    assert_denied(terminate())

    # Alice owns the ancestor -> may edit and terminate the manager below it
    set_auth(role="owner", user_uuid=alice)
    assert_granted(edit())
    assert_granted(terminate())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_moving_a_detail_requires_owning_the_destination(
    create_org_unit: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An owner may not move a detail into a unit they do not own
    owned = create_org_unit("owned")
    also_owned = create_org_unit("also-owned")
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)
    make_owner(alice, org_unit=(also_owned))
    manager = create_manager(owned)

    def edit(**fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateManager($input: ManagerUpdateInput!) {
                manager_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": manager,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns neither unit
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(org_unit=foreign))
    assert_denied(edit(org_unit=also_owned))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns the unit the manager sits on, but not the one it would move to
    assert_denied(edit(org_unit=foreign))
    # Alice owns both the unit it sits on and the one it moves to
    assert_granted(edit(org_unit=also_owned))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_related_units_is_gated_on_the_origin_unit(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # `related_units_update` gates on `origin`, not the units it relates to
    owned = create_org_unit("owned")
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)

    def relate(origin: str, destination: str) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateRelatedUnits($input: RelatedUnitsUpdateInput!) {
                related_units_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "origin": origin,
                        "destination": [destination],
                        "validity": {"from": "2021-01-01"},
                    }
                }
            ),
        )

    # A stranger owns no origin to work from
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(relate(owned, foreign))
    assert_denied(relate(foreign, owned))

    set_auth(role="owner", user_uuid=alice)
    # The origin is the unit Alice owns, whatever it is related to
    assert_granted(relate(owned, foreign))
    # An origin Alice does not own
    assert_denied(relate(foreign, owned))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_update_requires_all_items_owned(
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Every item in a batch must be owned, so one foreign engagement denies it
    owned = create_org_unit("owned")
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)

    def engagement_for(org_unit: UUID, user_key: str) -> UUID:
        return create_engagement(
            {
                "user_key": user_key,
                "person": str(bob),
                "org_unit": str(org_unit),
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    ours = engagement_for(owned, "ours")
    theirs = engagement_for(foreign, "theirs")

    def update(*engagements: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateEngagements($input: [EngagementUpdateInput!]!) {
                engagements_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {"uuid": engagement, "validity": {"from": "2021-01-01"}}
                        for engagement in engagements
                    ]
                }
            ),
        )

    # A stranger owns no unit the engagements sit on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(update(ours))
    assert_denied(update(ours, theirs))

    # Every engagement in the batch sits on the unit Alice owns
    set_auth(role="owner", user_uuid=alice)
    assert_granted(update(ours))
    # One of them does not, so the batch is denied whole
    assert_denied(update(ours, theirs))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_cannot_delete_a_detail(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # `ituser_delete` names its object by a bare `uuid` rather than an input, and
    # ownership is read off an input, so an owner is granted no delete at all
    make_owner(alice, person=bob)
    ituser = create_ituser(
        {
            "user_key": "acct",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2020-01-01"},
        }
    )

    def delete() -> GQLResponse:
        return graphapi_post(
            """
            mutation DeleteITUser($uuid: UUID!) {
                ituser_delete(uuid: $uuid) { uuid }
            }
            """,
            variables=jsonable_encoder({"uuid": ituser}),
        )

    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(delete())

    set_auth(role="owner", user_uuid=alice)
    assert_denied(delete())


# The IT system the envvar below names, so the test must create that very one
AUTHORITATIVE = "44444444-4444-4444-4444-444444444444"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar({"KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS": AUTHORITATIVE})
async def test_owner_through_authoritative_it_system(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    # Configured, the rules reach the caller through an IT user holding the
    # token's uuid as an external id
    external_id = "33333333-3333-3333-3333-333333333333"
    make_owner(alice, person=bob)
    create_itsystem(
        {
            "uuid": AUTHORITATIVE,
            "user_key": "authoritative",
            "name": "Authoritative",
            "validity": {"from": "2020-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "alice",
            "itsystem": AUTHORITATIVE,
            "person": str(alice),
            "external_id": external_id,
            "validity": {"from": "2020-01-01"},
        }
    )

    # The external id names Alice, who owns Bob
    set_auth(role="owner", user_uuid=external_id)
    assert_granted(employee_update(bob))

    # Her own employee uuid is no external id there, so it names nobody
    set_auth(role="owner", user_uuid=alice)
    assert_denied(employee_update(bob))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_vacant_seat_grants_nobody(
    set_auth: SetAuth,
    alice: UUID,
    create_org_unit: Callable[..., UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    unit = create_org_unit("owned")
    make_owner(alice, org_unit=unit)
    # A second seat on the very same unit, naming nobody
    create_owner(
        {
            "owner": None,
            "org_unit": str(unit),
            "validity": {"from": "2020-01-01"},
        }
    )

    def rename() -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": unit,
                        "validity": {"from": "2021-01-01"},
                        "name": "Renamed",
                    }
                }
            ),
        )

    # The vacant seat is nobody's, so a stranger gains nothing from it
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(rename())

    # And it does not cost Alice the ownership her own seat grants
    set_auth(role="owner", user_uuid=alice)
    assert_granted(rename())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_terminates_only_what_it_owns(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    root = create_org_unit("root")
    # `root` itself cannot be terminated: its owner relation is a detail
    child = create_org_unit("child", root)
    unowned_unit = create_org_unit("unowned")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def terminate_unit(unit: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateOU($input: OrganisationUnitTerminateInput!) {
                org_unit_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": unit, "to": "2021-01-01"}}),
        )

    def terminate_person(person: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminatePerson($input: EmployeeTerminateInput!) {
                employee_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": person, "to": "2021-01-01"}}),
        )

    # A stranger owns no unit and no person, not even the ones Alice owns
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate_unit(unowned_unit))
    assert_denied(terminate_person(carol))
    assert_denied(terminate_unit(child))
    assert_denied(terminate_person(bob))

    # Alice owns `child` through `root`, and Bob directly, and nothing else
    set_auth(role="owner", user_uuid=alice)
    assert_denied(terminate_unit(unowned_unit))
    assert_denied(terminate_person(carol))
    assert_granted(terminate_unit(child))
    assert_granted(terminate_person(bob))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_without_a_token_uuid_is_denied(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    """An owner token carrying no uuid names no employee, so it owns nothing."""
    make_owner(alice, person=bob)

    set_auth(role="owner", user_uuid=None)
    assert_denied(employee_update(bob))
