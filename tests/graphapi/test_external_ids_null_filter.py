# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_it_user_external_ids_null_filter(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    """`external_ids: null` returns only it-users without an external_id."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "Active Directory",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )
    create_ituser(
        {
            "user_key": "with-external-id",
            "external_id": "ext-1",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    without_external_id_uuid = create_ituser(
        {
            "user_key": "without-external-id",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    query = """
        query ReadITUsers {
            itusers(filter: {external_ids: null}) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data is not None
    returned = {UUID(o["uuid"]) for o in response.data["itusers"]["objects"]}
    assert returned == {without_external_id_uuid}
