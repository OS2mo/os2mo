# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.fixture
def read_ituser_user_keys(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[str]]:
    def inner(filter: dict[str, Any]) -> set[str]:
        query = """
            query ReadITUsers($filter: ITUserFilter) {
                itusers(filter: $filter) {
                    objects {
                        current {
                            user_key
                        }
                    }
                }
            }
        """
        response = graphapi_post(query, {"filter": filter})
        assert response.errors is None
        assert response.data
        return {
            obj["current"]["user_key"]
            for obj in response.data["itusers"]["objects"]
            if obj["current"] is not None
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all three returned.
        ({}, {"alice_primary", "bob_non_primary", "bob_unset"}),
        # `primary: null` selects itusers without a primary class set.
        ({"primary": None}, {"bob_unset"}),
        # `primary: {}` selects itusers with any primary class set.
        ({"primary": {}}, {"alice_primary", "bob_non_primary"}),
        # Filter by primary class user_key.
        ({"primary": {"user_keys": ["primary"]}}, {"alice_primary"}),
        # Filter by non-primary class user_key.
        ({"primary": {"user_keys": ["non-primary"]}}, {"bob_non_primary"}),
        # Filter by both class user_keys.
        (
            {"primary": {"user_keys": ["primary", "non-primary"]}},
            {"alice_primary", "bob_non_primary"},
        ),
        # Filter by a non-existent class yields nothing.
        ({"primary": {"user_keys": ["nonexistent"]}}, set()),
    ],
)
def test_ituser_primary_filter(
    read_ituser_user_keys: Callable[[dict[str, Any]], set[str]],
    create_ituser: Callable[[dict[str, Any]], UUID],
    primary_class: UUID,
    non_primary_class: UUID,
    itsystem: UUID,
    alice: UUID,
    bob: UUID,
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that itusers can be filtered by primary class."""
    create_ituser(
        {
            "user_key": "alice_primary",
            "itsystem": str(itsystem),
            "person": str(alice),
            "primary": str(primary_class),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "bob_non_primary",
            "itsystem": str(itsystem),
            "person": str(bob),
            "primary": str(non_primary_class),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "bob_unset",
            "itsystem": str(itsystem),
            "person": str(bob),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_ituser_user_keys(filter) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_ituser_primary_survives_validity_extension(
    graphapi_post: GraphAPIPost,
    create_ituser: Callable[[dict[str, Any]], UUID],
    primary_class: UUID,
    itsystem: UUID,
    person: UUID,
) -> None:
    """An edit that only touches validity must not drop the primary relation."""
    ituser_uuid = create_ituser(
        {
            "user_key": "primary_ituser",
            "itsystem": str(itsystem),
            "person": str(person),
            "primary": str(primary_class),
            "validity": {"from": "2024-01-01", "to": "2024-12-31"},
        }
    )

    # Extend validity without touching primary.
    update_response = graphapi_post(
        """
        mutation UpdateITUser($input: ITUserUpdateInput!) {
            ituser_update(input: $input) {
                uuid
            }
        }
        """,
        {
            "input": {
                "uuid": str(ituser_uuid),
                "validity": {"from": "2024-01-01", "to": "2025-12-31"},
            }
        },
    )
    assert update_response.errors is None

    read_response = graphapi_post(
        """
        query Read($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    validities {
                        primary_uuid
                        validity {from to}
                    }
                }
            }
        }
        """,
        {"uuid": str(ituser_uuid)},
    )
    assert read_response.errors is None
    assert read_response.data
    validities = one(read_response.data["itusers"]["objects"])["validities"]
    validity = one(validities)
    assert validity == {
        "primary_uuid": str(primary_class),
        "validity": {
            "from": "2024-01-01T00:00:00+01:00",
            "to": "2025-12-31T00:00:00+01:00",
        },
    }
