# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from more_itertools import first
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the ITSystem data model."""
    query = """
        query {
            itsystems {
                objects {
                    objects {
                        uuid
                        name
                        system_type
                        type
                        user_key
                        uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_create(graphapi_post) -> None:
    """Test that we can create new itsystems."""

    existing_itsystem_uuids = {
        UUID("0872fb72-926d-4c5c-a063-ff800b8ee697"),
        UUID("14466fb0-f9de-439c-a6c2-b3262c367da7"),
        UUID("59c135c9-2b15-41cc-97c8-b5dff7180beb"),
    }

    # Verify existing state
    query = """
        query ReadITSystems {
            itsystems {
                objects {
                    current {
                        uuid
                        user_key
                        name
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {
        UUID(x["current"]["uuid"]): x["current"]
        for x in response.data["itsystems"]["objects"]
    }
    assert itsystem_map.keys() == existing_itsystem_uuids

    # Create new itsystem
    mutation = """
        mutation CreateITSystem($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                uuid
            }
        }
    """
    it_system_uuid = UUID("624e4f57-0a36-4751-9982-51ef37457ebc")
    response = graphapi_post(
        mutation,
        {
            "input": {
                "uuid": str(it_system_uuid),
                "user_key": "my_user_key",
                "name": "my_name",
                "validity": {"from": "1930-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["itsystem_create"]["uuid"])
    assert new_uuid == it_system_uuid

    # Verify modified state
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {
        UUID(x["current"]["uuid"]): x["current"]
        for x in response.data["itsystems"]["objects"]
    }
    assert itsystem_map.keys() == existing_itsystem_uuids | {new_uuid}

    # Verify new object
    itsystem = itsystem_map[new_uuid]
    assert itsystem["name"] == "my_name"
    assert itsystem["user_key"] == "my_user_key"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_infinite_dates(graphapi_post) -> None:
    """Test that itsystems allow for infinite validity dates."""

    # Create new itsystem
    mutation = """
        mutation CreateInfiniteITSystem {
          itsystem_create(
            input: {
              user_key: "to_infinity",
              name: "and beyond!",
              validity: {from: null, to: null},
            }
          ) {
            uuid
          }
        }
    """
    response = graphapi_post(mutation)
    assert response.errors is None
    uuid = UUID(response.data["itsystem_create"]["uuid"])

    # Validate it(-system)
    query = """
        query ReadInfiniteITSystem($uuid: UUID!) {
          itsystems(filter: {uuids: [$uuid]}) {
            objects {
              current {
                uuid
                user_key
                name
                validity {
                  from
                  to
                }
              }
            }
          }
        }
    """
    response = graphapi_post(query, variables={"uuid": str(uuid)})
    assert response.errors is None
    itsystem = one(response.data["itsystems"]["objects"])["current"]
    assert itsystem["validity"] == {"from": None, "to": None}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_update(graphapi_post) -> None:
    """Test that we can update itsystems."""
    existing_itsystem_uuid = UUID("0872fb72-926d-4c5c-a063-ff800b8ee697")

    # Verify existing state
    query = """
        query ReadITSystems($uuids: [UUID!]) {
            itsystems(filter: {uuids: $uuids}) {
                objects {
                    current {
                        uuid
                        user_key
                        name
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuids": str(existing_itsystem_uuid)})
    assert response.errors is None
    assert response.data
    itsystem = one(response.data["itsystems"]["objects"])["current"]
    assert itsystem["name"] == "Lokal Rammearkitektur"

    # Update new itsystem
    mutation = """
        mutation UpdateITSystem($input: ITSystemUpdateInput!) {
            itsystem_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        mutation,
        {
            "input": {
                "user_key": "my_user_key",
                "name": "my_name",
                "uuid": str(existing_itsystem_uuid),
                "validity": {"from": "1930-01-01"},
            },
        },
    )
    assert response.errors is None
    assert response.data
    edit_uuid = UUID(response.data["itsystem_update"]["uuid"])
    assert edit_uuid == existing_itsystem_uuid

    # Verify modified state
    response = graphapi_post(query, {"uuids": str(existing_itsystem_uuid)})
    assert response.errors is None
    assert response.data
    itsystem = one(response.data["itsystems"]["objects"])["current"]
    assert itsystem["name"] == "my_name"
    assert itsystem["user_key"] == "my_user_key"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_itsystem_delete(graphapi_post) -> None:
    """Test that we can delete an itsystem."""

    existing_itsystem_uuids = {
        UUID("0872fb72-926d-4c5c-a063-ff800b8ee697"),
        UUID("14466fb0-f9de-439c-a6c2-b3262c367da7"),
        UUID("59c135c9-2b15-41cc-97c8-b5dff7180beb"),
    }

    # Verify existing state
    query = """
        query ReadITSystems {
            itsystems {
                objects {
                    current {
                        uuid
                        user_key
                        name
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {
        UUID(x["current"]["uuid"]): x for x in response.data["itsystems"]["objects"]
    }
    assert itsystem_map.keys() == existing_itsystem_uuids

    # Delete itsystem
    mutation = """
        mutation DeleteITSystem($uuid: UUID!) {
            itsystem_delete(uuid: $uuid) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"uuid": str(first(existing_itsystem_uuids))})
    assert response.errors is None
    assert response.data
    deleted_uuid = UUID(response.data["itsystem_delete"]["uuid"])

    # Verify modified state
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {
        UUID(x["current"]["uuid"]): x for x in response.data["itsystems"]["objects"]
    }
    assert itsystem_map.keys() == existing_itsystem_uuids - {deleted_uuid}
