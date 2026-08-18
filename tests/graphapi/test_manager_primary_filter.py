# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.fixture
def read_manager_user_keys(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[str]]:
    def inner(filter: dict[str, Any]) -> set[str]:
        query = """
            query ReadManagers($filter: ManagerFilter) {
                managers(filter: $filter) {
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
            for obj in response.data["managers"]["objects"]
            if obj["current"] is not None
        }

    return inner


@pytest.fixture
def read_manager_primary(
    graphapi_post: GraphAPIPost,
) -> Callable[[UUID], list[dict[str, Any]]]:
    """Read the primary class of a manager across all of its validities."""

    def inner(uuid: UUID) -> list[dict[str, Any]]:
        query = """
            query ReadManagerPrimary($uuid: UUID!) {
                managers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                    objects {
                        validities {
                            primary_response {
                                current {
                                    user_key
                                }
                            }
                            validity {from to}
                        }
                    }
                }
            }
        """
        response = graphapi_post(query, {"uuid": str(uuid)})
        assert response.errors is None
        assert response.data
        return one(response.data["managers"]["objects"])["validities"]

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_manager_create_with_primary(
    read_manager_primary: Callable[[UUID], list[dict[str, Any]]],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    primary_class: UUID,
    person: UUID,
) -> None:
    """A manager created with a primary class reads it back."""
    org_unit = create_org_unit("root")
    manager_uuid = create_manager_raw(
        {
            "manager_level": str(uuid4()),
            "manager_type": str(uuid4()),
            "responsibility": [],
            "org_unit": str(org_unit),
            "person": str(person),
            "primary": str(primary_class),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_manager_primary(manager_uuid) == [
        {
            "primary_response": {"current": {"user_key": "primary"}},
            "validity": {"from": "2024-01-01T00:00:00+01:00", "to": None},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_manager_update_primary(
    graphapi_post: GraphAPIPost,
    read_manager_primary: Callable[[UUID], list[dict[str, Any]]],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    primary_class: UUID,
    non_primary_class: UUID,
    person: UUID,
) -> None:
    """An update from a future date leaves the preceding primary class intact."""
    org_unit = create_org_unit("root")
    manager_uuid = create_manager_raw(
        {
            "manager_level": str(uuid4()),
            "manager_type": str(uuid4()),
            "responsibility": [],
            "org_unit": str(org_unit),
            "person": str(person),
            "primary": str(non_primary_class),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_manager_primary(manager_uuid) == [
        {
            "primary_response": {"current": {"user_key": "non-primary"}},
            "validity": {"from": "2024-01-01T00:00:00+01:00", "to": None},
        }
    ]

    # Change the primary class from 2025 onwards only.
    update_response = graphapi_post(
        """
        mutation UpdateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
        """,
        {
            "input": {
                "uuid": str(manager_uuid),
                "primary": str(primary_class),
                "validity": {"from": "2025-01-01"},
            }
        },
    )
    assert update_response.errors is None

    # The 2024 period keeps the old class, the 2025 period gets the new one.
    assert read_manager_primary(manager_uuid) == [
        {
            "primary_response": {"current": {"user_key": "non-primary"}},
            "validity": {
                "from": "2024-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
        {
            "primary_response": {"current": {"user_key": "primary"}},
            "validity": {"from": "2025-01-01T00:00:00+01:00", "to": None},
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all three returned.
        ({}, {"alice_primary", "bob_non_primary", "bob_unset"}),
        # `primary: null` selects managers without a primary class set.
        ({"primary": None}, {"bob_unset"}),
        # `primary: {}` selects managers with any primary class set.
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
def test_manager_primary_filter(
    read_manager_user_keys: Callable[[dict[str, Any]], set[str]],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    primary_class: UUID,
    non_primary_class: UUID,
    alice: UUID,
    bob: UUID,
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that managers can be filtered by primary class."""
    org_unit = create_org_unit("root")

    def create(user_key: str, person: UUID, primary: UUID | None) -> None:
        create_manager_raw(
            {
                "user_key": user_key,
                "manager_level": str(uuid4()),
                "manager_type": str(uuid4()),
                "responsibility": [],
                "org_unit": str(org_unit),
                "person": str(person),
                "primary": str(primary) if primary else None,
                "validity": {"from": "2024-01-01"},
            }
        )

    create("alice_primary", alice, primary_class)
    create("bob_non_primary", bob, non_primary_class)
    create("bob_unset", bob, None)

    assert read_manager_user_keys(filter) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_manager_primary_survives_validity_extension(
    graphapi_post: GraphAPIPost,
    read_manager_primary: Callable[[UUID], list[dict[str, Any]]],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    primary_class: UUID,
    person: UUID,
) -> None:
    """An edit that only touches validity must not drop the primary relation."""
    org_unit = create_org_unit("root")
    manager_uuid = create_manager_raw(
        {
            "manager_level": str(uuid4()),
            "manager_type": str(uuid4()),
            "responsibility": [],
            "org_unit": str(org_unit),
            "person": str(person),
            "primary": str(primary_class),
            "validity": {"from": "2024-01-01", "to": "2024-12-31"},
        }
    )

    expected: dict[str, Any] = {
        "primary_response": {"current": {"user_key": "primary"}},
        "validity": {
            "from": "2024-01-01T00:00:00+01:00",
            "to": "2024-12-31T00:00:00+01:00",
        },
    }
    assert read_manager_primary(manager_uuid) == [expected]

    # Extend validity without touching primary.
    update_response = graphapi_post(
        """
        mutation UpdateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
        """,
        {
            "input": {
                "uuid": str(manager_uuid),
                "validity": {"from": "2024-01-01", "to": "2025-12-31"},
            }
        },
    )
    assert update_response.errors is None

    # Only the end date moved; everything else is unchanged.
    assert read_manager_primary(manager_uuid) == [
        {
            **expected,
            "validity": {
                **expected["validity"],
                "to": "2025-12-31T00:00:00+01:00",
            },
        }
    ]
