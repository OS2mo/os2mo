# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

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
            obj["current"]["user_key"] for obj in response.data["itusers"]["objects"]
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # No rolebinding filter: every ituser is returned.
        ({}, {"bound", "unbound"}),
        # `rolebinding: null` selects itusers without any rolebinding.
        ({"rolebinding": None}, {"unbound"}),
        # `rolebinding: {}` selects itusers with any rolebinding.
        ({"rolebinding": {}}, {"bound"}),
        # Filter by rolebinding user_key.
        ({"rolebinding": {"user_keys": ["bound_admin"]}}, {"bound"}),
        # Filter by rolebinding role.
        ({"rolebinding": {"role": {"user_keys": ["admin"]}}}, {"bound"}),
        # Filter by a different role yields nothing.
        ({"rolebinding": {"role": {"user_keys": ["reader"]}}}, set()),
        # Filter by a non-existent rolebinding user_key yields nothing.
        ({"rolebinding": {"user_keys": ["nonexistent"]}}, set()),
    ],
)
def test_ituser_rolebinding_filter(
    role_facet: UUID,
    read_ituser_user_keys: Callable[[dict[str, Any]], set[str]],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that itusers can be filtered by rolebinding."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "2024-01-01"},
        }
    )
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_class(
        {
            "user_key": "reader",
            "name": "Read-only",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )
    bound_ituser_uuid = create_ituser(
        {
            "user_key": "bound",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "unbound",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    create_rolebinding(
        {
            "user_key": "bound_admin",
            "ituser": str(bound_ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_ituser_user_keys(filter) == expected
