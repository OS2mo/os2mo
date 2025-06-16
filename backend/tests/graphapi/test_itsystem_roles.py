# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_roles(graphapi_post: GraphAPIPost) -> None:
    """Test that we can create and read itsystem roles."""
    # Read the role facet UUID
    facet_uuid_query = """
        query ReadFacetUUID($user_key: String!) {
            facets(filter: {user_keys: [$user_key]}) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(facet_uuid_query, {"user_key": "role"})
    assert response.errors is None
    assert response.data
    role_facet_uuid = one(response.data["facets"]["objects"])["uuid"]

    # Create new itsystem
    itsystem_create_mutation = """
        mutation CreateITSystem($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                uuid
            }
        }
    """
    itsystem_uuid = UUID("624e4f57-0a36-4751-9982-51ef37457ebc")
    itsystem_user_key = "suila"
    itsystem_name = "Suila-tapit"
    response = graphapi_post(
        itsystem_create_mutation,
        {
            "input": {
                "uuid": str(itsystem_uuid),
                "user_key": itsystem_user_key,
                "name": itsystem_name,
                "validity": {"from": "2024-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["itsystem_create"]["uuid"])
    assert new_uuid == itsystem_uuid

    # Read the new itsystem along with its (non-existent) roles
    query = """
        query ReadITSystem($uuid: UUID!) {
            itsystems(filter: {uuids: [$uuid]}) {
                objects {
                    uuid
                    current {
                        user_key
                        name
                        roles {
                            uuid
                            current {
                                user_key
                                name
                            }
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(itsystem_uuid)})
    assert response.errors is None
    assert response.data
    itsystem = one(response.data["itsystems"]["objects"])
    assert itsystem == {
        "uuid": str(itsystem_uuid),
        "current": {
            "user_key": itsystem_user_key,
            "name": itsystem_name,
            "roles": [],
        },
    }

    # Create a rolebinding role
    class_create_mutation = """
        mutation CreateRole($input: ClassCreateInput!) {
            class_create(input: $input) {
                uuid
            }
        }
    """
    class_uuid = UUID("64cf30fb-8819-4be2-9f62-39fc6cb9b169")
    class_user_key = "admin"
    class_name = "Administrator"
    response = graphapi_post(
        class_create_mutation,
        {
            "input": {
                "uuid": str(class_uuid),
                "user_key": class_user_key,
                "name": class_name,
                "facet_uuid": str(role_facet_uuid),
                "it_system_uuid": str(itsystem_uuid),
                "validity": {"from": "2024-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["class_create"]["uuid"])
    assert new_uuid == class_uuid

    # Read the itsystem again along with its now existing role
    query = """
        query ReadITSystem($uuid: UUID!) {
            itsystems(filter: {uuids: [$uuid]}) {
                objects {
                    uuid
                    current {
                        user_key
                        name
                        roles {
                            uuid
                            current {
                                user_key
                                name
                            }
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(itsystem_uuid)})
    assert response.errors is None
    assert response.data
    itsystem = one(response.data["itsystems"]["objects"])
    assert itsystem == {
        "uuid": str(itsystem_uuid),
        "current": {
            "user_key": itsystem_user_key,
            "name": itsystem_name,
            "roles": [
                {
                    "uuid": str(class_uuid),
                    "current": {
                        "user_key": class_user_key,
                        "name": class_name,
                    },
                }
            ],
        },
    }
