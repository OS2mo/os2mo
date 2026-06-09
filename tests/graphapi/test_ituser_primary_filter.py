# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.fixture
def primary_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {
            "user_key": "primary_type",
            "validity": {"from": "1970-01-01"},
        }
    )


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
def test_ituser_primary_filter(
    primary_facet: UUID,
    read_ituser_user_keys: Callable[[dict[str, Any]], set[str]],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    """Test that itusers can be filtered by primary class."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "ad",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    primary_class_uuid = create_class(
        {
            "user_key": "primary",
            "name": "Primary",
            "facet_uuid": str(primary_facet),
            "scope": "3000",
            "validity": {"from": "2024-01-01"},
        }
    )
    non_primary_class_uuid = create_class(
        {
            "user_key": "non-primary",
            "name": "Non-primary",
            "facet_uuid": str(primary_facet),
            "scope": "0",
            "validity": {"from": "2024-01-01"},
        }
    )
    alice_uuid = create_person({"given_name": "Alice", "surname": "A"})
    bob_uuid = create_person({"given_name": "Bob", "surname": "B"})
    create_ituser(
        {
            "user_key": "alice_primary",
            "itsystem": str(itsystem_uuid),
            "person": str(alice_uuid),
            "primary": str(primary_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "bob_non_primary",
            "itsystem": str(itsystem_uuid),
            "person": str(bob_uuid),
            "primary": str(non_primary_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "bob_unset",
            "itsystem": str(itsystem_uuid),
            "person": str(bob_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    # No filter: all three returned.
    assert read_ituser_user_keys({}) == {
        "alice_primary",
        "bob_non_primary",
        "bob_unset",
    }
    # `primary: null` selects itusers without a primary class set.
    assert read_ituser_user_keys({"primary": None}) == {"bob_unset"}
    # `primary: {}` selects itusers with any primary class set.
    assert read_ituser_user_keys({"primary": {}}) == {
        "alice_primary",
        "bob_non_primary",
    }
    # Filter by primary class UUID.
    assert read_ituser_user_keys({"primary": {"uuids": [str(primary_class_uuid)]}}) == {
        "alice_primary"
    }
    # Filter by non-primary class UUID.
    assert read_ituser_user_keys(
        {"primary": {"uuids": [str(non_primary_class_uuid)]}}
    ) == {"bob_non_primary"}
    # Filter by both class UUIDs.
    assert read_ituser_user_keys(
        {"primary": {"uuids": [str(primary_class_uuid), str(non_primary_class_uuid)]}}
    ) == {"alice_primary", "bob_non_primary"}
    # Filter by class user_key.
    assert read_ituser_user_keys({"primary": {"user_keys": ["primary"]}}) == {
        "alice_primary"
    }
    # Filter by a non-existent class yields nothing.
    assert read_ituser_user_keys({"primary": {"user_keys": ["nonexistent"]}}) == set()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_ituser_primary_survives_validity_extension(
    primary_facet: UUID,
    graphapi_post: GraphAPIPost,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    """An edit that only touches validity must not drop the primary relation.

    Regression: ITSYSTEM_FIELDS in mora/mapping.py previously omitted
    PRIMARY_FIELD, so ensure_bounds did not carry the existing primary across
    the extended period.
    """
    itsystem_uuid = create_itsystem(
        {
            "user_key": "ad",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    primary_class_uuid = create_class(
        {
            "user_key": "primary",
            "name": "Primary",
            "facet_uuid": str(primary_facet),
            "scope": "3000",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person({"given_name": "Alice", "surname": "A"})
    ituser_uuid = create_ituser(
        {
            "user_key": "alice_primary",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "primary": str(primary_class_uuid),
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

    # Inspect every validity period: primary must be set throughout.
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
    validities = read_response.data["itusers"]["objects"][0]["validities"]
    assert validities, "expected at least one validity period"
    for v in validities:
        assert v["primary_uuid"] == str(primary_class_uuid), (
            f"primary not preserved across validity {v['validity']}"
        )
