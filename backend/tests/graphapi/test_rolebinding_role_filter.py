# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_role_filter(
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
) -> None:
    """Test that we can filter by rolebindings on itusers."""
    # Create new itsystem
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "2024-01-01"},
        }
    )

    # Create a rolebinding role
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    reader_class_uuid = create_class(
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

    ituser_uuid = create_ituser(
        {
            "user_key": "xylia",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_rolebinding_uuids({})
    assert result == set()

    admin_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_admin",
            "ituser": str(ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    reader_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_reader",
            "ituser": str(ituser_uuid),
            "role": str(reader_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_rolebinding_uuids({})
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(admin_class_uuid)]}},
    )
    assert result == {admin_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(reader_class_uuid)]}},
    )
    assert result == {reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(admin_class_uuid), str(reader_class_uuid)]}},
    )
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"it_system": {"uuids": [str(itsystem_uuid)]}}},
    )
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}
