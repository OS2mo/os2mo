# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_engagement_itusers(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit_uuid = create_org_unit("test_org_unit", None)
    person_uuid = create_person(None)
    engagement_uuid = create_engagement(
        {
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    it_system_uuid = create_itsystem(
        {
            "user_key": "test_system",
            "name": "Test System",
            "validity": {"from": "2010-01-01"},
        }
    )
    it_user_uuid = create_ituser(
        {
            "user_key": "test_user",
            "itsystem": str(it_system_uuid),
            "person": str(person_uuid),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2010-01-01"},
        }
    )

    query = """
        query($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        itusers {
                            registrations {
                                uuid
                            }
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, variables={"uuid": str(engagement_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["engagements"]["objects"])
    ituser = one(obj["current"]["itusers"])
    registration = one(ituser["registrations"])
    assert registration["uuid"] == str(it_user_uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_itsystem_roles(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    it_system_uuid = create_itsystem(
        {
            "user_key": "test_system",
            "name": "Test System",
            "validity": {"from": "2010-01-01"},
        }
    )
    role_uuid = create_class(
        {
            "facet_uuid": "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7",
            "user_key": "test_role",
            "name": "Test Role",
            "it_system_uuid": str(it_system_uuid),
            "validity": {"from": "2010-01-01"},
        }
    )

    query = """
        query($uuid: UUID!) {
            itsystems(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        roles {
                            registrations {
                                uuid
                            }
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, variables={"uuid": str(it_system_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["itsystems"]["objects"])
    role = one(obj["current"]["roles"])
    registration = one(role["registrations"])
    assert registration["uuid"] == str(role_uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_ituser_engagements(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit_uuid = create_org_unit("test_org_unit", None)
    person_uuid = create_person(None)
    engagement_uuid = create_engagement(
        {
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    it_system_uuid = create_itsystem(
        {
            "user_key": "test_system",
            "name": "Test System",
            "validity": {"from": "2010-01-01"},
        }
    )
    it_user_uuid = create_ituser(
        {
            "user_key": "test_user",
            "itsystem": str(it_system_uuid),
            "person": str(person_uuid),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2010-01-01"},
        }
    )

    query = """
        query($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        engagements {
                            registrations {
                                uuid
                            }
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, variables={"uuid": str(it_user_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["itusers"]["objects"])
    engagement = one(obj["current"]["engagements"])
    registration = one(engagement["registrations"])
    assert registration["uuid"] == str(engagement_uuid)
