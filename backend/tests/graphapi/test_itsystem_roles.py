# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.fixture
def read_facet_uuid(graphapi_post: GraphAPIPost) -> Callable[[str], UUID]:
    def inner(user_key: str) -> UUID:
        facet_uuid_query = """
            query ReadFacetUUID($user_key: String!) {
                facets(filter: {user_keys: [$user_key]}) {
                    objects {
                        uuid
                    }
                }
            }
        """
        response = graphapi_post(facet_uuid_query, {"user_key": user_key})
        assert response.errors is None
        assert response.data
        facet_uuid = one(response.data["facets"]["objects"])["uuid"]
        return facet_uuid

    return inner


@pytest.fixture
def create_itsystem(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        itsystem_create_mutation = """
            mutation CreateITSystem($input: ITSystemCreateInput!) {
                itsystem_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(itsystem_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        itsystem_uuid = UUID(response.data["itsystem_create"]["uuid"])
        return itsystem_uuid

    return inner


@pytest.fixture
def create_class(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        class_create_mutation = """
            mutation CreateRole($input: ClassCreateInput!) {
                class_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(class_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        class_uuid = UUID(response.data["class_create"]["uuid"])
        return class_uuid

    return inner


@pytest.fixture
def read_itsystem(graphapi_post: GraphAPIPost) -> Callable[[UUID], dict[str, Any]]:
    def inner(uuid: UUID) -> dict[str, Any]:
        query = """
            query ReadITSystem($uuid: UUID!) {
                itsystems(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                    objects {
                        uuid
                        validities {
                            user_key
                            name
                            roles {
                                uuid
                                validities {
                                    user_key
                                    name
                                }
                            }
                        }
                    }
                }
            }
        """
        response = graphapi_post(query, {"uuid": str(uuid)})
        assert response.errors is None
        assert response.data
        itsystem = one(response.data["itsystems"]["objects"])
        return itsystem

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_roles(
    read_facet_uuid: Callable[[str], UUID],
    read_itsystem: Callable[[UUID], dict[str, Any]],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
) -> None:
    """Test that we can create and read itsystem roles."""
    # Read the role facet UUID
    role_facet_uuid = read_facet_uuid("role")

    # Create new itsystem
    itsystem_uuid = UUID("624e4f57-0a36-4751-9982-51ef37457ebc")
    itsystem_user_key = "suila"
    itsystem_name = "Suila-tapit"
    new_uuid = create_itsystem(
        {
            "uuid": str(itsystem_uuid),
            "user_key": itsystem_user_key,
            "name": itsystem_name,
            "validity": {"from": "2024-01-01"},
        }
    )
    assert new_uuid == itsystem_uuid

    # Read the new itsystem along with its (non-existent) roles
    assert read_itsystem(itsystem_uuid) == {
        "uuid": str(itsystem_uuid),
        "validities": [
            {
                "user_key": itsystem_user_key,
                "name": itsystem_name,
                "roles": [],
            }
        ],
    }

    # Create a rolebinding role
    class_uuid = UUID("64cf30fb-8819-4be2-9f62-39fc6cb9b169")
    class_user_key = "admin"
    class_name = "Administrator"
    new_uuid = create_class(
        {
            "uuid": str(class_uuid),
            "user_key": class_user_key,
            "name": class_name,
            "facet_uuid": str(role_facet_uuid),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    assert new_uuid == class_uuid

    # Read the itsystem again along with its now existing role
    assert read_itsystem(itsystem_uuid) == {
        "uuid": str(itsystem_uuid),
        "validities": [
            {
                "user_key": itsystem_user_key,
                "name": itsystem_name,
                "roles": [
                    {
                        "uuid": str(class_uuid),
                        "validities": [
                            {
                                "user_key": class_user_key,
                                "name": class_name,
                            }
                        ],
                    }
                ],
            }
        ],
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "class_start,class_end",
    [
        # Past
        (datetime(1970, 1, 1), datetime(1980, 1, 1)),
        # Current
        (datetime(1970, 1, 1), None),
        (datetime(1970, 1, 1), datetime(3000, 1, 1)),
        # Future
        (datetime(2970, 1, 1), None),
        (datetime(2970, 1, 1), datetime(3000, 1, 1)),
    ],
)
@pytest.mark.parametrize(
    "itsystem_start,itsystem_end",
    [
        # Past
        (datetime(1970, 1, 1), datetime(1980, 1, 1)),
        # Current
        (datetime(1970, 1, 1), None),
        (datetime(1970, 1, 1), datetime(3000, 1, 1)),
        # Future
        (datetime(2970, 1, 1), None),
        (datetime(2970, 1, 1), datetime(3000, 1, 1)),
    ],
)
def test_itsystem_roles_validities(
    read_facet_uuid: Callable[[str], UUID],
    read_itsystem: Callable[[UUID], dict[str, Any]],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    class_start: datetime,
    class_end: datetime | None,
    itsystem_start: datetime,
    itsystem_end: datetime | None,
) -> None:
    """Test that we can read role UUIDs whatever the validity of roles."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {
                "from": itsystem_start.isoformat(),
                "to": itsystem_end.isoformat() if itsystem_end else None,
            },
        }
    )
    # Create a rolebinding role
    class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(read_facet_uuid("role")),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {
                "from": class_start.isoformat(),
                "to": class_end.isoformat() if class_end else None,
            },
        }
    )
    # Read the itsystem and check that we can see the role UUID
    assert read_itsystem(itsystem_uuid) == {
        "uuid": ANY,
        "validities": [
            {
                "user_key": ANY,
                "name": ANY,
                "roles": [{"uuid": str(class_uuid), "validities": ANY}],
            }
        ],
    }
