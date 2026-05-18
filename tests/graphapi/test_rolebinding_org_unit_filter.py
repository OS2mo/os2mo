# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_org_unit_filter(
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
) -> None:
    """Test that rolebindings can be filtered by org_unit."""
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
    ituser_uuid = create_ituser(
        {
            "user_key": "xylia",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    alpha_unit_uuid = create_org_unit("alpha")
    beta_unit_uuid = create_org_unit("beta")

    alpha_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "alpha_admin",
            "ituser": str(ituser_uuid),
            "role": str(role_class_uuid),
            "org_unit": str(alpha_unit_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    beta_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "beta_admin",
            "ituser": str(ituser_uuid),
            "role": str(role_class_uuid),
            "org_unit": str(beta_unit_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    assert read_rolebinding_uuids({}) == {
        alpha_rolebinding_uuid,
        beta_rolebinding_uuid,
    }

    assert read_rolebinding_uuids(
        {"org_unit": {"uuids": [str(alpha_unit_uuid)]}},
    ) == {alpha_rolebinding_uuid}

    assert read_rolebinding_uuids(
        {"org_unit": {"uuids": [str(beta_unit_uuid)]}},
    ) == {beta_rolebinding_uuid}

    assert read_rolebinding_uuids(
        {"org_unit": {"uuids": [str(alpha_unit_uuid), str(beta_unit_uuid)]}},
    ) == {alpha_rolebinding_uuid, beta_rolebinding_uuid}
