# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of what an owner may touch over GraphQL."""

from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder

from tests.conftest import ACTIVE_DIRECTORY_UUID
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


# The IT system the owner rules are patched to name, so the test must create
# that very one
AUTHORITATIVE = str(ACTIVE_DIRECTORY_UUID)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "it_system_patched_owner_policy")
async def test_owner_through_authoritative_it_system(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    employee_update: Callable[[UUID | str], GQLResponse],
) -> None:
    # Patched, the rules reach the caller through an IT user holding the
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_ignores_aliases(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    """The policies key off `info.field_name`, the real name, never the alias."""
    owned = create_org_unit("owned")
    unowned = create_org_unit("unowned")
    make_owner(alice, org_unit=owned)

    def rename(unit: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
                not_a_mutator: org_unit_update(input: $input) { uuid }
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

    set_auth(role="owner", user_uuid=alice)
    # `not_a_mutator` has no owner rule, so an alias-keyed check would deny
    # everything; these follow `org_unit_update`'s rule instead
    assert_granted(rename(owned))
    assert_denied(rename(unowned))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_grants_mutations_only(
    set_auth: SetAuth,
    alice: UUID,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ownership only ever grants mutations, never a query."""
    set_auth(role="owner", user_uuid=alice)
    assert_denied(
        graphapi_post(
            """
            query FetchEvent($filter: EventFilter!) {
                event_fetch(filter: $filter) { token }
            }
            """,
            variables=jsonable_encoder({"filter": {"listener": uuid4()}}),
        )
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_addresses_require_every_unit_or_person_owned(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Each address in the batch links a unit or a person, and all must be owned
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)
    # `address_create` reads the address type's `scope`, so it must be real
    facet = create_facet(
        {"user_key": "address_type", "validity": {"from": "2000-01-01"}}
    )
    email = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "email",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2000-01-01"},
        }
    )

    def create(*links: dict[str, UUID]) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateAddresses($input: [AddressCreateInput!]!) {
                addresses_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {
                            "address_type": email,
                            "value": "someone@example.org",
                            "validity": {"from": "2021-01-01"},
                            **link,
                        }
                        for link in links
                    ]
                }
            ),
        )

    # A stranger owns no unit and no person in the batch
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create({"org_unit": child}, {"person": bob}))
    assert_denied(create({"person": bob}))
    assert_denied(create())

    # Alice owns `child` through `root`, and Bob, and nothing else
    set_auth(role="owner", user_uuid=alice)
    # A unit owned through its ancestor and an owned person -> granted, and the
    # batch creates an address for each
    response = create({"org_unit": child}, {"person": bob})
    assert_granted(response)
    assert response.data
    assert len(response.data["addresses_create"]) == 2
    # The deprecated `employee` names the person just as well as `person`
    assert_granted(create({"employee": bob}))
    # One unit is not owned -> the whole batch is denied
    assert_denied(create({"org_unit": child}, {"org_unit": foreign}))
    # One person is not owned -> the whole batch is denied
    assert_denied(create({"person": carol}, {"person": bob}))
    # An empty batch has nothing to own, so it is denied rather than
    # vacuously granted
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_terminates_an_association_through_its_unit_or_person(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_association: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An association links both a unit and a person, and owning either will do
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def association_for(org_unit: UUID, person: UUID) -> UUID:
        return create_association(
            {
                "org_unit": str(org_unit),
                "person": str(person),
                "association_type": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    on_owned_unit = association_for(child, carol)
    of_owned_person = association_for(foreign, bob)
    unowned = association_for(foreign, carol)

    def terminate(association: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateAssociation($input: AssociationTerminateInput!) {
                association_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"uuid": association, "to": "2050-01-01"}}
            ),
        )

    # A stranger owns neither the units nor the people
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(on_owned_unit))
    assert_denied(terminate(of_owned_person))
    assert_denied(terminate(unowned))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns neither the unit nor the person of this one
    assert_denied(terminate(unowned))
    # It sits on `child`, which Alice owns through `root`
    assert_granted(terminate(on_owned_unit))
    # It sits on a unit Alice does not own, but it is Bob's, whom she owns
    assert_granted(terminate(of_owned_person))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_itassociation_create_is_gated_on_the_unit(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An IT-association must name its unit, so the unit is what must be owned
    # and owning its person is never consulted
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
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

    def create(org_unit: UUID, person: UUID, ituser: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateITAssociation($input: ITAssociationCreateInput!) {
                itassociation_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "org_unit": org_unit,
                        "person": person,
                        "it_user": ituser,
                        "job_function": uuid4(),
                        "validity": {"from": "2021-01-01"},
                    }
                }
            ),
        )

    # A stranger owns no unit to create on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(root, carol, carols))
    assert_denied(create(child, carol, carols))
    assert_denied(create(foreign, bob, bobs))

    set_auth(role="owner", user_uuid=alice)
    # On `foreign`, which Alice does not own, whether or not she owns the person
    assert_denied(create(foreign, bob, bobs))
    assert_denied(create(foreign, carol, carols))
    # On `root`, which Alice owns, even for Carol, whom she does not
    assert_granted(create(root, carol, carols))
    # On `child`, which Alice owns through `root`
    assert_granted(create(child, carol, carols))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_itassociation_update_requires_owning_the_destination(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_itassociation: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # The IT-association must be owned, and so must any unit it is moved to.
    # Its update cannot name a person
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    also_owned = create_org_unit("also-owned")
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, org_unit=also_owned)
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

    def itassociation_for(org_unit: UUID, person: UUID) -> UUID:
        return create_itassociation(
            {
                "org_unit": str(org_unit),
                "person": str(person),
                "it_user": str(ituser_for(person)),
                "job_function": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    on_owned_unit = itassociation_for(child, carol)
    of_owned_person = itassociation_for(foreign, bob)
    unowned = itassociation_for(foreign, carol)

    def edit(itassociation: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateITAssociation($input: ITAssociationUpdateInput!) {
                itassociation_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": itassociation,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns no IT-association and no unit to move one to
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(on_owned_unit, user_key="changed"))
    assert_denied(edit(of_owned_person, user_key="changed"))
    assert_denied(edit(on_owned_unit, org_unit=also_owned))
    assert_denied(edit(unowned, org_unit=also_owned))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns the IT-association, but not the unit it would move to
    assert_denied(edit(on_owned_unit, org_unit=foreign))
    # Alice owns the unit it would move to, but not the IT-association
    assert_denied(edit(unowned, org_unit=also_owned))
    # Owning Bob is no licence to name a unit Alice does not own, not even the
    # one his IT-association already sits on
    assert_denied(edit(of_owned_person, org_unit=foreign))
    # Naming no unit leaves the IT-association alone to decide
    assert_denied(edit(unowned, user_key="changed"))
    assert_granted(edit(of_owned_person, user_key="changed"))
    assert_granted(edit(on_owned_unit, user_key="changed"))
    # Alice owns both the IT-association and the unit it moves to
    assert_granted(edit(on_owned_unit, org_unit=also_owned))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_terminates_an_itassociation_through_its_unit_or_person(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_itassociation: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An IT-association is an association, so owning its unit or person will do
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
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

    def itassociation_for(org_unit: UUID, person: UUID) -> UUID:
        return create_itassociation(
            {
                "org_unit": str(org_unit),
                "person": str(person),
                "it_user": str(ituser_for(person)),
                "job_function": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    on_owned_unit = itassociation_for(child, carol)
    of_owned_person = itassociation_for(foreign, bob)
    unowned = itassociation_for(foreign, carol)

    def terminate(itassociation: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateITAssociation($input: ITAssociationTerminateInput!) {
                itassociation_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"uuid": itassociation, "to": "2050-01-01"}}
            ),
        )

    # A stranger owns neither the units nor the people
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(on_owned_unit))
    assert_denied(terminate(of_owned_person))
    assert_denied(terminate(unowned))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns neither the unit nor the person of this one
    assert_denied(terminate(unowned))
    # It sits on `child`, which Alice owns through `root`
    assert_granted(terminate(on_owned_unit))
    # It sits on a unit Alice does not own, but it is Bob's, whom she owns
    assert_granted(terminate(of_owned_person))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_create_engagements_requires_all_units_owned(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An engagement always names its unit, so the unit decides, not the person
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    owned = create_org_unit("owned")
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, org_unit=owned)
    make_owner(alice, person=bob)

    def create(*items: tuple[UUID, UUID]) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateEngagements($input: [EngagementCreateInput!]!) {
                engagements_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {
                            "person": person,
                            "org_unit": org_unit,
                            "engagement_type": uuid4(),
                            "job_function": uuid4(),
                            "validity": {"from": "2020-01-01"},
                        }
                        for org_unit, person in items
                    ]
                }
            ),
        )

    # A stranger owns no unit in the batch
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create((owned, carol), (child, carol)))
    assert_denied(create((foreign, bob)))
    assert_denied(create())

    set_auth(role="owner", user_uuid=alice)
    # Alice owns `owned` directly and `child` through its ancestor `root`
    assert_granted(create((owned, carol), (child, carol)))
    # One unit is not owned -> the whole batch is denied, wherever it comes
    assert_denied(create((owned, carol), (foreign, carol)))
    assert_denied(create((foreign, carol), (owned, carol)))
    # Owning the person does not help, as the unit named decides
    assert_denied(create((foreign, bob)))
    # An empty batch has nothing to own, so it is denied
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_create_managers_requires_all_units_owned(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A manager always names its unit, so the unit decides, not the person
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    owned = create_org_unit("owned")
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, org_unit=owned)
    make_owner(alice, person=bob)

    def create(*items: tuple[UUID, UUID | None]) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateManagers($input: [ManagerCreateInput!]!) {
                managers_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {
                            "person": person,
                            "org_unit": org_unit,
                            "manager_level": uuid4(),
                            "manager_type": uuid4(),
                            "responsibility": [],
                            "validity": {"from": "2020-01-01"},
                        }
                        for org_unit, person in items
                    ]
                }
            ),
        )

    # A stranger owns no unit in the batch
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create((owned, carol), (child, None)))
    assert_denied(create((foreign, bob)))
    assert_denied(create())

    set_auth(role="owner", user_uuid=alice)
    # Alice owns `owned` directly and `child` through its ancestor `root`, and
    # a vacant manager seat names no person but still names its unit
    assert_granted(create((owned, carol), (child, None)))
    # One unit is not owned -> the whole batch is denied, wherever it comes
    assert_denied(create((owned, carol), (foreign, None)))
    assert_denied(create((foreign, None), (owned, carol)))
    # Owning the person does not help, as the unit named decides
    assert_denied(create((foreign, bob)))
    # An empty batch has nothing to own, so it is denied
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_ituser_create_on_person_or_unit(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    itsystem: UUID,
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # An IT user belongs to exactly one of a person and a unit, which decides
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def create(**fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateITUser($input: ITUserCreateInput!) {
                ituser_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "user_key": str(uuid4()),
                        "itsystem": itsystem,
                        "validity": {"from": "2020-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns no person and no unit
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(person=bob))
    assert_denied(create(person=carol))
    assert_denied(create(org_unit=root))
    assert_denied(create(org_unit=child))
    assert_denied(create(org_unit=foreign))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns Bob, but not Carol
    assert_granted(create(person=bob))
    assert_denied(create(person=carol))
    # Alice owns `root` directly and `child` through it, but not `foreign`
    assert_granted(create(org_unit=root))
    assert_granted(create(org_unit=child))
    assert_denied(create(org_unit=foreign))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_terminates_an_ituser_through_its_unit_or_person(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    itsystem: UUID,
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Owning either the person or the unit of an IT user grants terminating it
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def ituser_for(**fields: Any) -> UUID:
        return create_ituser(
            jsonable_encoder(
                {
                    "user_key": str(uuid4()),
                    "itsystem": itsystem,
                    "validity": {"from": "2020-01-01"},
                    **fields,
                }
            )
        )

    bobs = ituser_for(person=bob)
    carols = ituser_for(person=carol)
    on_root = ituser_for(org_unit=root)
    on_child = ituser_for(org_unit=child)
    on_foreign = ituser_for(org_unit=foreign)

    def terminate(ituser: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateITUser($input: ITUserTerminateInput!) {
                ituser_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": ituser, "to": "2021-01-01"}}),
        )

    # A stranger owns no person and no unit
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(bobs))
    assert_denied(terminate(carols))
    assert_denied(terminate(on_root))
    assert_denied(terminate(on_child))
    assert_denied(terminate(on_foreign))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns neither Carol nor `foreign`
    assert_denied(terminate(carols))
    assert_denied(terminate(on_foreign))
    # Alice owns Bob, the person of the IT user
    assert_granted(terminate(bobs))
    # Alice owns `root`, the unit of the IT user, directly
    assert_granted(terminate(on_root))
    # ... and `child` through its ancestor `root`
    assert_granted(terminate(on_child))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_kle_create_requires_owning_the_unit(
    create_org_unit: Callable[..., UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A KLE annotates a unit; Alice owns `owned` directly and `child` through
    # its ancestor `root`
    owned = create_org_unit("owned")
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)
    make_owner(alice, org_unit=root)

    def create(org_unit: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateKLE($input: KLECreateInput!) {
                kle_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "org_unit": org_unit,
                        "kle_number": uuid4(),
                        "kle_aspects": [uuid4()],
                        "validity": {"from": "2020-01-01"},
                    }
                }
            ),
        )

    # A stranger owns no unit to annotate
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(owned))
    assert_denied(create(child))
    assert_denied(create(foreign))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns `owned` directly
    assert_granted(create(owned))
    # ... and `child` through its ancestor `root`
    assert_granted(create(child))
    # She does not own `foreign`
    assert_denied(create(foreign))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_kle_update_requires_owning_both_units(
    create_org_unit: Callable[..., UUID],
    create_kle: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Alice owns `owned` and `also_owned` directly, and `child` through `root`
    owned = create_org_unit("owned")
    also_owned = create_org_unit("also-owned")
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)
    make_owner(alice, org_unit=also_owned)
    make_owner(alice, org_unit=root)

    def kle_on(org_unit: UUID) -> UUID:
        return create_kle(
            {
                "org_unit": str(org_unit),
                "kle_number": str(uuid4()),
                "kle_aspects": [str(uuid4())],
                "validity": {"from": "2020-01-01"},
            }
        )

    ours = kle_on(owned)
    nested = kle_on(child)
    theirs = kle_on(foreign)

    def edit(kle: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateKLE($input: KLEUpdateInput!) {
                kle_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": kle,
                        "user_key": "changed",
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns neither the units the KLEs sit on nor any to move them to
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(ours))
    assert_denied(edit(nested))
    assert_denied(edit(theirs))
    assert_denied(edit(ours, org_unit=also_owned))
    assert_denied(edit(theirs, org_unit=owned))

    set_auth(role="owner", user_uuid=alice)
    # Naming no unit, the unit the KLE sits on alone decides
    assert_granted(edit(ours))
    # ... which Alice may own through an ancestor
    assert_granted(edit(nested))
    # Alice does not own the unit `theirs` sits on
    assert_denied(edit(theirs))
    # Alice owns the KLE, but not the unit it would move away to
    assert_denied(edit(ours, org_unit=foreign))
    # Alice owns the unit, but not the KLE that would move into it
    assert_denied(edit(theirs, org_unit=owned))
    # Alice owns both the unit the KLE sits on and the one it moves to
    assert_granted(edit(ours, org_unit=also_owned))
    # ... and the unit moved to may be owned through an ancestor
    assert_granted(edit(ours, org_unit=child))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_kle_terminate_requires_owning_the_unit(
    create_org_unit: Callable[..., UUID],
    create_kle: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
    alice: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A KLE links no person, so only its unit (or an ancestor) can be owned;
    # Alice owns `owned` directly and `child` through `root`
    owned = create_org_unit("owned")
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)
    make_owner(alice, org_unit=root)

    def kle_on(org_unit: UUID) -> UUID:
        return create_kle(
            {
                "org_unit": str(org_unit),
                "kle_number": str(uuid4()),
                "kle_aspects": [str(uuid4())],
                "validity": {"from": "2020-01-01"},
            }
        )

    ours = kle_on(owned)
    nested = kle_on(child)
    theirs = kle_on(foreign)

    def terminate(kle: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateKLE($input: KLETerminateInput!) {
                kle_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": kle, "to": "2050-01-01"}}),
        )

    # A stranger owns no unit any of the KLEs sit on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(ours))
    assert_denied(terminate(nested))
    assert_denied(terminate(theirs))

    set_auth(role="owner", user_uuid=alice)
    # Alice does not own the unit `theirs` sits on
    assert_denied(terminate(theirs))
    # She owns the unit `ours` sits on directly
    assert_granted(terminate(ours))
    # ... and the one `nested` sits on through its ancestor `root`
    assert_granted(terminate(nested))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_leave_update_follows_the_person(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A leave links only a person, so owning the unit of its engagement is no
    # way to own it: Alice owns `unit` and Bob and Dave, but not Carol
    unit = create_org_unit("unit")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    dave = create_person({"given_name": "Dave", "surname": "Dahl"})
    make_owner(alice, org_unit=unit)
    make_owner(alice, person=bob)
    make_owner(alice, person=dave)

    def engagement_for(person: UUID) -> UUID:
        return create_engagement(
            {
                "person": str(person),
                "org_unit": str(unit),
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    def leave_for(person: UUID) -> UUID:
        return create_leave(
            {
                "person": str(person),
                "engagement": str(engagement_for(person)),
                "leave_type": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    bobs = leave_for(bob)
    carols = leave_for(carol)
    # Dave needs an engagement of his own for a leave to be moved to him
    engagement_for(dave)

    def edit(leave: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateLeave($input: LeaveUpdateInput!) {
                leave_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": leave,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns nobody, and no unit either
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(bobs))
    assert_denied(edit(carols))
    assert_denied(edit(bobs, person=dave))
    assert_denied(edit(carols, person=bob))

    set_auth(role="owner", user_uuid=alice)
    # Naming no person, the leave alone decides: Bob's is owned through Bob
    assert_granted(edit(bobs, user_key="changed"))
    # Carol's engagement sits on `unit`, but her leave links no unit to own
    assert_denied(edit(carols, user_key="changed"))
    # Moving Bob's leave away to Carol, whom Alice does not own
    assert_denied(edit(bobs, person=carol))
    # Moving Carol's leave in to Bob, though Alice does not own the leave
    assert_denied(edit(carols, person=bob))
    # Moving Bob's leave to Dave: Alice owns both the leave and its new person
    assert_granted(edit(bobs, person=dave))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_leave_terminate_follows_the_person(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Alice owns Bob and the unit both engagements sit on, but not Carol
    unit = create_org_unit("unit")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=unit)
    make_owner(alice, person=bob)

    def leave_for(person: UUID) -> UUID:
        engagement = create_engagement(
            {
                "person": str(person),
                "org_unit": str(unit),
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )
        return create_leave(
            {
                "person": str(person),
                "engagement": str(engagement),
                "leave_type": str(uuid4()),
                "validity": {"from": "2020-01-01"},
            }
        )

    bobs = leave_for(bob)
    carols = leave_for(carol)

    def terminate(leave: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateLeave($input: LeaveTerminateInput!) {
                leave_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": leave, "to": "2030-01-01"}}),
        )

    # A stranger owns nobody, and no unit either
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(bobs))
    assert_denied(terminate(carols))

    set_auth(role="owner", user_uuid=alice)
    # Carol's engagement sits on `unit`, but her leave links no unit to own
    assert_denied(terminate(carols))
    # Bob's leave is owned through Bob
    assert_granted(terminate(bobs))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_employee_create_naming_a_uuid(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    create_person: Callable[[dict[str, Any] | None], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A create naming a uuid is checked against the person already there
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, person=bob)
    fresh = uuid4()

    def create(uuid: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreatePerson($input: EmployeeCreateInput!) {
                employee_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"uuid": uuid, "given_name": "New", "surname": "Comer"}}
            ),
        )

    # A stranger owns nobody, and a fresh uuid names nobody to own
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(bob))
    assert_denied(create(carol))
    assert_denied(create(fresh))

    set_auth(role="owner", user_uuid=alice)
    # Alice does not own Carol
    assert_denied(create(carol))
    # Nobody owns a person who does not exist yet
    assert_denied(create(fresh))
    # Alice owns Bob, so she may create over him
    assert_granted(create(bob))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_creates_owners_only_for_what_it_owns(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A seat is owned through the unit or the person it sits on, not its holder
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def create(**fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateOwner($input: OwnerCreateInput!) {
                owner_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"validity": {"from": "2021-01-01"}, **fields}}
            ),
        )

    # A stranger owns no unit and no person
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(org_unit=root))
    assert_denied(create(org_unit=child))
    assert_denied(create(person=bob))
    assert_denied(create(org_unit=foreign))
    assert_denied(create(person=carol))

    set_auth(role="owner", user_uuid=alice)
    # A vacant seat on `root`, which Alice owns directly -> granted
    assert_granted(create(org_unit=root))
    # Appointing Carol to `child`, which Alice owns through `root` -> granted
    assert_granted(create(org_unit=child, owner=carol))
    # Appointing Carol to Bob, whom Alice owns -> granted
    assert_granted(create(person=bob, owner=carol))
    # A unit or a person Alice does not own -> denied
    assert_denied(create(org_unit=foreign))
    assert_denied(create(person=carol))
    # Naming herself the holder does not make it hers to create
    assert_denied(create(org_unit=foreign, owner=alice))
    assert_denied(create(person=carol, owner=alice))
    # A named unit decides alone, so an owned person does not make up for it
    assert_denied(create(org_unit=foreign, person=bob))
    # A seat on neither leaves nothing to own -> denied
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_moves_owners_only_between_what_it_owns(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Both the seat and the unit or person it is moved to must be owned
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def seat(**fields: Any) -> UUID:
        return create_owner(
            jsonable_encoder({"validity": {"from": "2020-01-01"}, **fields})
        )

    # Vacant seats, so they make nobody an owner of anything
    on_child = seat(org_unit=child)
    on_bob = seat(person=bob)
    on_foreign = seat(org_unit=foreign)
    on_carol = seat(person=carol)

    def edit(owner: UUID, **fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateOwner($input: OwnerUpdateInput!) {
                owner_update(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "uuid": owner,
                        "validity": {"from": "2021-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns no seat and nothing to move one to
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(edit(on_child, org_unit=root))
    assert_denied(edit(on_bob, person=bob))
    assert_denied(edit(on_foreign, org_unit=child))
    assert_denied(edit(on_carol, person=bob))
    assert_denied(edit(on_foreign))

    set_auth(role="owner", user_uuid=alice)
    # Alice owns the seats on `child` and Bob, but not where they would move to
    assert_denied(edit(on_child, org_unit=foreign))
    assert_denied(edit(on_bob, person=carol))
    # Alice owns where the seats would move to, but not the seats themselves
    assert_denied(edit(on_foreign, org_unit=child))
    assert_denied(edit(on_carol, person=bob))
    # Naming neither unit nor person, the seat alone decides, and it is not hers
    assert_denied(edit(on_foreign))
    # Alice owns Bob, whom the seat sits on and stays on
    assert_granted(edit(on_bob, person=bob))
    # Alice owns the seat on `child` through `root`, and `root` it moves up to
    assert_granted(edit(on_child, org_unit=root))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_terminates_owners_only_of_what_it_owns(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A seat is owned through the unit or the person it sits on, not its holder
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    carol = create_person({"given_name": "Carol", "surname": "Carlsen"})
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)

    def seat(**fields: Any) -> UUID:
        return create_owner(
            jsonable_encoder({"validity": {"from": "2020-01-01"}, **fields})
        )

    # Vacant seats, so they make nobody an owner of anything
    on_child = seat(org_unit=child)
    on_bob = seat(person=bob)
    on_foreign = seat(org_unit=foreign)
    on_carol = seat(person=carol)
    # Bob holds this one, which makes him, not Alice, the owner of `foreign`
    held_by_bob = seat(org_unit=foreign, owner=bob)

    def terminate(owner: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateOwner($input: OwnerTerminateInput!) {
                owner_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder({"input": {"uuid": owner, "to": "2030-01-01"}}),
        )

    # A stranger owns no unit and no person a seat sits on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(on_child))
    assert_denied(terminate(on_bob))
    assert_denied(terminate(on_foreign))
    assert_denied(terminate(on_carol))
    assert_denied(terminate(held_by_bob))

    set_auth(role="owner", user_uuid=alice)
    # Seats on a unit or a person Alice does not own -> denied
    assert_denied(terminate(on_foreign))
    assert_denied(terminate(on_carol))
    # Owning Bob, the holder, does not make his seat hers
    assert_denied(terminate(held_by_bob))
    # The seat on `child`, which Alice owns through `root` -> granted
    assert_granted(terminate(on_child))
    # The seat on Bob, whom Alice owns -> granted
    assert_granted(terminate(on_bob))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_rolebinding_create_is_gated_on_its_unit(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    role_facet: UUID,
    create_org_unit: Callable[..., UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # A role-binding links no person, so only the unit it binds on counts
    # Alice owns `root` (and thus `child`), and Bob, whose IT-user gets the role
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)
    role = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem),
            "validity": {"from": "2010-01-01"},
        }
    )
    ituser = create_ituser(
        {
            "user_key": "bob",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2010-01-01"},
        }
    )

    def create(**fields: Any) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateRoleBinding($input: RoleBindingCreateInput!) {
                rolebinding_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": {
                        "ituser": ituser,
                        "role": role,
                        "validity": {"from": "2020-01-01"},
                        **fields,
                    }
                }
            ),
        )

    # A stranger owns no unit to bind a role on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(org_unit=root))
    assert_denied(create(org_unit=child))
    assert_denied(create(org_unit=foreign))
    assert_denied(create(org_unit=None))

    set_auth(role="owner", user_uuid=alice)
    # On the unit Alice owns -> granted
    assert_granted(create(org_unit=root))
    # On a unit below it -> granted, through its ancestor
    assert_granted(create(org_unit=child))
    # On a unit she does not own -> denied, though she owns the IT-user's person
    assert_denied(create(org_unit=foreign))
    # A global role-binding (null unit) has no unit to own -> denied
    assert_denied(create(org_unit=None))
    # An absent `org_unit` defaults to null, a global role-binding too -> denied
    assert_denied(create())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_rolebinding_terminate_is_gated_on_its_unit_only(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    role_facet: UUID,
    create_org_unit: Callable[..., UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # Alice owns `root` (and thus `child`), and Bob, whose IT-user has the roles
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=root)
    make_owner(alice, person=bob)
    role = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem),
            "validity": {"from": "2010-01-01"},
        }
    )
    ituser = create_ituser(
        {
            "user_key": "bob",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2010-01-01"},
        }
    )

    def rolebinding_on(org_unit: UUID | None) -> UUID:
        return create_rolebinding(
            jsonable_encoder(
                {
                    "ituser": ituser,
                    "role": role,
                    "org_unit": org_unit,
                    "validity": {"from": "2020-01-01"},
                }
            )
        )

    on_root = rolebinding_on(root)
    on_child = rolebinding_on(child)
    on_foreign = rolebinding_on(foreign)
    global_rolebinding = rolebinding_on(None)

    def terminate(rolebinding: UUID) -> GQLResponse:
        return graphapi_post(
            """
            mutation TerminateRoleBinding($input: RoleBindingTerminateInput!) {
                rolebinding_terminate(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {"input": {"uuid": rolebinding, "to": "2050-01-01"}}
            ),
        )

    # A stranger owns no unit the role-bindings sit on
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(terminate(on_root))
    assert_denied(terminate(on_child))
    assert_denied(terminate(on_foreign))
    assert_denied(terminate(global_rolebinding))

    set_auth(role="owner", user_uuid=alice)
    # Owning the IT-user's person grants nothing: only the unit counts
    assert_denied(terminate(on_foreign))
    # A global role-binding sits on no unit, so nobody owns it
    assert_denied(terminate(global_rolebinding))
    # On the unit Alice owns -> granted
    assert_granted(terminate(on_root))
    # On a unit below it -> granted, through its ancestor
    assert_granted(terminate(on_child))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_owner_bulk_rolebindings_require_every_unit_owned(
    set_auth: SetAuth,
    alice: UUID,
    bob: UUID,
    itsystem: UUID,
    role_facet: UUID,
    create_org_unit: Callable[..., UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    make_owner: Callable[..., None],
    graphapi_post: GraphAPIPost,
) -> None:
    # rolebindings_create takes a list; the owner must own every item's unit
    owned = create_org_unit("owned")
    child = create_org_unit("child", owned)
    foreign = create_org_unit("foreign")
    make_owner(alice, org_unit=owned)
    role = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem),
            "validity": {"from": "2010-01-01"},
        }
    )
    ituser = create_ituser(
        {
            "user_key": "bob",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2010-01-01"},
        }
    )

    def create(*units: UUID | None) -> GQLResponse:
        return graphapi_post(
            """
            mutation CreateRoleBindings($input: [RoleBindingCreateInput!]!) {
                rolebindings_create(input: $input) { uuid }
            }
            """,
            variables=jsonable_encoder(
                {
                    "input": [
                        {
                            "ituser": ituser,
                            "role": role,
                            "org_unit": unit,
                            "validity": {"from": "2020-01-01"},
                        }
                        for unit in units
                    ]
                }
            ),
        )

    # A stranger owns no unit in the batch
    set_auth(role="owner", user_uuid=uuid4())
    assert_denied(create(owned, child))
    assert_denied(create(owned, foreign))
    assert_denied(create(None))
    assert_denied(create())

    set_auth(role="owner", user_uuid=alice)
    # Every unit in the batch is owned, `child` through its ancestor -> granted
    assert_granted(create(owned, child))
    # One unit is not owned -> the whole batch is denied, wherever it comes
    assert_denied(create(owned, foreign))
    assert_denied(create(foreign, owned))
    # A batch in which no item names a unit leaves nothing to own -> denied
    assert_denied(create(None))
    # An empty batch yields no checks, so it is denied rather than
    # vacuously granted
    assert_denied(create())
