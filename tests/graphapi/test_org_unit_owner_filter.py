# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # The owner sub-filter is an `OwnerFilter`; filter by the owner person
        # through its own nested `owner` field.
        (
            {"owner": {"owner": {"user_keys": ["owner-1"]}}},
            {"owned-1", "owned-both"},
        ),
        (
            {"owner": {"owner": {"user_keys": ["owner-2"]}}},
            {"owned-2", "owned-both"},
        ),
        # The owner-person `user_keys` is OR'ed: owned by owner-1 OR owner-2.
        (
            {"owner": {"owner": {"user_keys": ["owner-1", "owner-2"]}}},
            {"owned-1", "owned-2", "owned-both"},
        ),
        # An owner that owns no org-units.
        (
            {"owner": {"owner": {"user_keys": ["unowned"]}}},
            set(),
        ),
        # A non-existent owner.
        (
            {"owner": {"owner": {"user_keys": ["does-not-exist"]}}},
            set(),
        ),
        # An empty owner filter matches every org-unit that has any owner.
        (
            {"owner": {}},
            {"owned-1", "owned-2", "owned-both"},
        ),
        # The owner filter AND's with the rest of the org-unit filter: only
        # org-units owned by owner-1 AND in the explicit user-key set.
        (
            {
                "owner": {"owner": {"user_keys": ["owner-1"]}},
                "user_keys": ["owned-both"],
            },
            {"owned-both"},
        ),
        (
            {"owner": {"owner": {"user_keys": ["owner-1"]}}, "user_keys": ["owned-2"]},
            set(),
        ),
    ],
)
def test_org_unit_owner_filter(
    read_org_unit_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The org-unit `owner` filter returns the directly-owned org-units.

    Ownership graph (owner person -> owned org-units):
        owner-1 -> owned-1, owned-both
        owner-2 -> owned-2, owned-both
        unowned -> (owns nothing)
    """
    owners = {
        user_key: create_person(
            {"user_key": user_key, "given_name": "O", "surname": user_key}
        )
        for user_key in ("owner-1", "owner-2", "unowned")
    }
    owned = {
        user_key: create_org_unit(user_key)
        for user_key in ("owned-1", "owned-2", "owned-both")
    }

    def own(unit: str, owner: str) -> None:
        create_owner(
            {
                "org_unit": str(owned[unit]),
                "owner": str(owners[owner]),
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        )

    own("owned-1", "owner-1")
    own("owned-2", "owner-2")
    own("owned-both", "owner-1")
    own("owned-both", "owner-2")

    actual = read_org_unit_uuids(filter)
    assert actual == {owned[user_key] for user_key in expected}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_org_unit_owner_filter_by_owner_function(
    read_org_unit_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """The owner sub-filter is an `OwnerFilter`, so the owned org-unit can be
    selected by the owner org-function's own uuid.
    """
    owner = create_person({"given_name": "Owns", "surname": "Person"})
    org_unit = create_org_unit("owned")
    owner_function = create_owner(
        {
            "org_unit": str(org_unit),
            "owner": str(owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )

    actual = read_org_unit_uuids({"owner": {"uuids": [str(owner_function)]}})
    assert actual == {org_unit}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "org_unit_from,owner_from,matches",
    [
        # By default both gates are evaluated as of now, where they have expired.
        (None, None, False),
        # Both set within the validity period: the org-unit is matched.
        ("2020-06-01T00:00:00+01:00", "2020-06-01T00:00:00+01:00", True),
        # Only the ownership link is dated back; the owner org-function is still
        # evaluated as of now (expired) -> no match.
        ("2020-06-01T00:00:00+01:00", None, False),
        # Only the owner org-function is dated back; the ownership link is still
        # evaluated as of now (expired) -> no match.
        (None, "2020-06-01T00:00:00+01:00", False),
        # Both outside the validity period.
        ("2023-06-01T00:00:00+01:00", "2023-06-01T00:00:00+01:00", False),
    ],
)
def test_org_unit_owner_filter_respects_validity(
    read_org_unit_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    org_unit_from: str | None,
    owner_from: str | None,
    matches: bool,
) -> None:
    """The owner relation is only matched within its validity period.

    The owner sub-filter carries its own validity, so a historical ownership
    query must set `from_date` on both the org-unit filter (which gates the
    ownership link) and the nested owner filter (which gates the owner
    org-function itself).
    """
    owner = create_person({"given_name": "Temp", "surname": "Owner"})
    org_unit = create_org_unit("owned")
    create_owner(
        {
            "org_unit": str(org_unit),
            "owner": str(owner),
            "validity": {
                "from": "2020-01-01T00:00:00+01:00",
                "to": "2020-12-31T00:00:00+01:00",
            },
        }
    )

    # The ownership link (outer org-unit filter) and the owner org-function
    # itself (the `OwnerFilter`) are gated by separate `from_date`s; both must
    # fall within the validity period for a match.
    org_unit_filter: dict[str, Any] = {"owner": {"owner": {"uuids": [str(owner)]}}}
    if org_unit_from is not None:
        org_unit_filter["from_date"] = org_unit_from
    if owner_from is not None:
        org_unit_filter["owner"]["from_date"] = owner_from

    actual = read_org_unit_uuids(org_unit_filter)
    assert actual == ({org_unit} if matches else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_org_unit_owner_filter_nested(
    read_org_unit_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """The owner sub-filter recurses: an org-unit's owner can itself be filtered
    by who owns them.
    """
    grand_owner = create_person({"given_name": "Grand", "surname": "Owner"})
    owner = create_person({"given_name": "Mid", "surname": "Owner"})
    org_unit = create_org_unit("owned")

    # grand_owner owns owner; owner owns org_unit.
    create_owner(
        {
            "person": str(owner),
            "owner": str(grand_owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )
    create_owner(
        {
            "org_unit": str(org_unit),
            "owner": str(owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )

    # Org-units whose owner is in turn owned by grand_owner -> {org_unit}.
    actual = read_org_unit_uuids(
        {"owner": {"owner": {"owner": {"owner": {"uuids": [str(grand_owner)]}}}}}
    )
    assert actual == {org_unit}
