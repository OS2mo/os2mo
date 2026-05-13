# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_ituser_filter(
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
) -> None:
    """Test that rolebindings can be filtered by ituser."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "2024-01-01"},
        }
    )
    role_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
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

    alpha_ituser_uuid = create_ituser(
        {
            "user_key": "alpha",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    beta_ituser_uuid = create_ituser(
        {
            "user_key": "beta",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    alpha_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "alpha_admin",
            "ituser": str(alpha_ituser_uuid),
            "role": str(role_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    beta_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "beta_admin",
            "ituser": str(beta_ituser_uuid),
            "role": str(role_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_rolebinding_uuids({}) == {
        alpha_rolebinding_uuid,
        beta_rolebinding_uuid,
    }

    assert read_rolebinding_uuids(
        {"ituser": {"uuids": [str(alpha_ituser_uuid)]}},
    ) == {alpha_rolebinding_uuid}

    assert read_rolebinding_uuids(
        {"ituser": {"uuids": [str(beta_ituser_uuid)]}},
    ) == {beta_rolebinding_uuid}

    assert read_rolebinding_uuids(
        {"ituser": {"uuids": [str(alpha_ituser_uuid), str(beta_ituser_uuid)]}},
    ) == {alpha_rolebinding_uuid, beta_rolebinding_uuid}

    assert (
        read_rolebinding_uuids(
            {"ituser": {"user_keys": ["nonexistent"]}},
        )
        == set()
    )
