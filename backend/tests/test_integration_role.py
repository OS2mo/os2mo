# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost

userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
mock_uuid = "288ecae8-faa4-428f-872e-1ad1a466b330"
role_uuid = "1b20d0b9-96a0-42a6-b196-293bb86e62e8"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_rolebinding_read_and_terminate(graphapi_post: GraphAPIPost) -> None:
    GET_ROLEBINDING_QUERY = """
    query GetRoleBinding($filter: RoleBindingFilter!) {
      rolebindings(filter: $filter) {
        objects {
          validities {
            uuid
            role {
              uuid
            }
            ituser {
              uuid
            }
            validity {
              to
              from
            }
          }
        }
      }
    }
    """
    ituser_uuid = "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66"
    role_uuid = "0fa6073f-32c0-4f82-865f-adb622ca0b04"

    # Create role binding
    response = graphapi_post(
        """
        mutation CreateRoleBinding($ituser_uuid: UUID!, $role_uuid: UUID!) {
          rolebinding_create(
            input: {ituser: $ituser_uuid, role: $role_uuid, validity: {from: "2020-01-01"}, user_key: "test1"}
          ) {
            uuid
          }
        }
        """,
        variables={
            "ituser_uuid": ituser_uuid,
            "role_uuid": role_uuid,
        },
    )
    assert response.errors is None
    rolebinding_uuid = response.data["rolebinding_create"]["uuid"]
    assert rolebinding_uuid

    # Check that we can get rolebinding
    response = graphapi_post(
        GET_ROLEBINDING_QUERY,
        variables={
            "filter": {"user_keys": "test1"},
        },
    )
    assert response.errors is None
    assert one(one(response.data["rolebindings"]["objects"])["validities"]) == {
        "uuid": rolebinding_uuid,
        "role": [{"uuid": role_uuid}],
        "ituser": [{"uuid": ituser_uuid}],
        "validity": {"to": None, "from": "2020-01-01T00:00:00+01:00"},
    }

    # Terminate rolebinding
    response = graphapi_post(
        """
        mutation TerminateRoleBinding($uuid: UUID!) {
          rolebinding_terminate(
            input: {to: "2023-05-05", uuid: $uuid}
          ) {
            uuid
          }
        }
        """,
        variables={
            "uuid": rolebinding_uuid,
        },
    )
    assert response.errors is None

    # Check that we no longer find role binding
    response = graphapi_post(
        GET_ROLEBINDING_QUERY,
        variables={
            "filter": {"user_keys": "test1"},
        },
    )
    assert response.errors is None
    assert response.data["rolebindings"]["objects"] == []

    # Check that rolebinding is terminated
    response = graphapi_post(
        GET_ROLEBINDING_QUERY,
        variables={
            "filter": {"user_keys": "test1", "from_date": None, "to_date": None},
        },
    )
    assert response.errors is None
    assert one(one(response.data["rolebindings"]["objects"])["validities"]) == {
        "uuid": rolebinding_uuid,
        "role": [{"uuid": role_uuid}],
        "ituser": [{"uuid": ituser_uuid}],
        "validity": {
            "from": "2020-01-01T00:00:00+01:00",
            "to": "2023-05-05T00:00:00+02:00",
        },
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_rolebinding_edit(graphapi_post: GraphAPIPost) -> None:
    GET_ROLEBINDING_QUERY = """
    query GetRoleBinding($filter: RoleBindingFilter!) {
      rolebindings(filter: $filter) {
        objects {
          validities {
            uuid
            user_key
            role {
              uuid
            }
            ituser {
              uuid
            }
            validity {
              to
              from
            }
          }
        }
      }
    }
    """
    ituser_uuid = "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66"
    role_uuid = "0fa6073f-32c0-4f82-865f-adb622ca0b04"

    # Create role binding
    response = graphapi_post(
        """
        mutation CreateRoleBinding($ituser_uuid: UUID!, $role_uuid: UUID!) {
          rolebinding_create(
            input: {ituser: $ituser_uuid, user_key: "Originales", role: $role_uuid, validity: {from: "2020-01-01"}}
          ) {
            uuid
          }
        }
        """,
        variables={
            "ituser_uuid": ituser_uuid,
            "role_uuid": role_uuid,
        },
    )
    assert response.errors is None
    rolebinding_uuid = response.data["rolebinding_create"]["uuid"]
    assert rolebinding_uuid

    # Edit rolebinding
    response = graphapi_post(
        """
        mutation EditRoleBinding($uuid: UUID!, $ituser_uuid: UUID!) {
          rolebinding_update(
            input: {uuid: $uuid, ituser: $ituser_uuid, validity: {from: "2024-03-03"}, user_key: "Updaterino"}
          ) {
            uuid
          }
        }
        """,
        variables={
            "uuid": rolebinding_uuid,
            "ituser_uuid": ituser_uuid,
        },
    )
    assert response.errors is None
    edited_rolebinding_uuid = response.data["rolebinding_update"]["uuid"]
    assert rolebinding_uuid == edited_rolebinding_uuid

    # Check that we can get rolebinding
    response = graphapi_post(
        GET_ROLEBINDING_QUERY,
        variables={
            "filter": {"uuids": rolebinding_uuid, "from_date": None, "to_date": None},
        },
    )
    assert response.errors is None
    assert one(response.data["rolebindings"]["objects"])["validities"] == [
        {
            "uuid": rolebinding_uuid,
            "user_key": "Originales",
            "role": [{"uuid": role_uuid}],
            "ituser": [{"uuid": ituser_uuid}],
            "validity": {
                "from": "2020-01-01T00:00:00+01:00",
                "to": "2024-03-02T00:00:00+01:00",
            },
        },
        {
            "uuid": rolebinding_uuid,
            "user_key": "Updaterino",
            "role": [{"uuid": role_uuid}],
            "ituser": [{"uuid": ituser_uuid}],
            "validity": {"from": "2024-03-03T00:00:00+01:00", "to": None},
        },
    ]
