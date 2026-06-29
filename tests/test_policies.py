# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.db.policies import POLICYADMIN_UUID
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost

POLICYADMIN = str(POLICYADMIN_UUID)

DECLARE_POLICY = """
  mutation DeclarePolicy($input: PolicyDeclareInput!) {
    policy_declare(input: $input) {
      uuid
      name
      description
      start
      end
    }
  }
"""

READ_POLICIES = """
  query ReadPolicies {
    policies {
      objects {
        uuid
        name
        description
        start
        end
      }
    }
  }
"""

PAGINATE_POLICIES = """
  query PaginatePolicies($limit: int, $cursor: Cursor) {
    policies(limit: $limit, cursor: $cursor) {
      objects {
        uuid
        name
      }
      page_info {
        next_cursor
      }
    }
  }
"""

DELETE_POLICY = """
  mutation DeletePolicy($uuid: UUID!) {
    policy_delete(input: { uuid: $uuid })
  }
"""

NOT_FOUND_UUID = "d0d19f81-36e0-46bd-9be5-49d31b1e15a7"


def declare_policy(graphapi_post: GraphAPIPost, **input) -> GQLResponse:
    return graphapi_post(DECLARE_POLICY, variables={"input": input})


def read_policies(graphapi_post: GraphAPIPost) -> list[dict]:
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None
    return response.data["policies"]["objects"]


@pytest.mark.integration_test
async def test_policyadmin_is_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The migration inserts the policyadmin policy, so it is always present.
    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert POLICYADMIN in policies
    assert policies[POLICYADMIN]["name"] == "Policy Administrator"


@pytest.mark.integration_test
async def test_policyadmin_cannot_be_deleted(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = graphapi_post(DELETE_POLICY, variables={"uuid": POLICYADMIN})
    assert response.errors is not None

    # It is still there.
    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_create_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = declare_policy(
        graphapi_post,
        name="GDPR",
        description="Data protection policy",
        start="2024-01-01T00:00:00+00:00",
    )
    assert response.errors is None
    created = response.data["policy_declare"]
    assert created["name"] == "GDPR"
    assert created["description"] == "Data protection policy"
    assert created["end"] is None

    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert created["uuid"] in policies
    assert policies[created["uuid"]]["name"] == "GDPR"
    # The bootstrap policy coexists with the created one.
    assert POLICYADMIN in policies


@pytest.mark.integration_test
async def test_policy_declare_updates_existing(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    created = declare_policy(
        graphapi_post, name="Initial", start="2024-01-01T00:00:00+00:00"
    )
    uuid = created.data["policy_declare"]["uuid"]

    updated = declare_policy(
        graphapi_post,
        uuid=uuid,
        name="Renamed",
        description="now with a description",
        start="2024-01-01T00:00:00+00:00",
        end="2025-01-01T00:00:00+00:00",
    )
    assert updated.errors is None
    obj = updated.data["policy_declare"]
    assert obj["uuid"] == uuid
    assert obj["name"] == "Renamed"
    assert obj["description"] == "now with a description"
    assert obj["end"] is not None

    # Declaring with a uuid updates rather than creates: bootstrap + the one.
    assert len(read_policies(graphapi_post)) == 2


@pytest.mark.integration_test
async def test_policy_declare_unknown_uuid_fails(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = declare_policy(
        graphapi_post,
        uuid=NOT_FOUND_UUID,
        name="ghost",
        start="2024-01-01T00:00:00+00:00",
    )
    assert response.errors is not None


@pytest.mark.integration_test
async def test_policy_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    created = declare_policy(
        graphapi_post, name="ToDelete", start="2024-01-01T00:00:00+00:00"
    )
    uuid = created.data["policy_declare"]["uuid"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert uuid not in uuids
    # Deleting a normal policy leaves the bootstrap policy untouched.
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_pagination(graphapi_post: GraphAPIPost, empty_db) -> None:
    # Create a handful of policies to page through (plus the bootstrap one).
    created: set[str] = set()
    for i in range(5):
        response = declare_policy(
            graphapi_post, name=f"policy-{i}", start="2024-01-01T00:00:00+00:00"
        )
        assert response.errors is None
        created.add(response.data["policy_declare"]["uuid"])

    # Page through them two at a time using the keyset cursor.
    seen: list[str] = []
    cursor = None
    for _ in range(10):  # safety bound to avoid an infinite loop
        response = graphapi_post(
            PAGINATE_POLICIES, variables={"limit": 2, "cursor": cursor}
        )
        assert response.errors is None
        page = response.data["policies"]
        seen.extend(obj["uuid"] for obj in page["objects"])
        cursor = page["page_info"]["next_cursor"]
        if cursor is None:
            break
    else:  # pragma: no cover
        raise AssertionError("pagination did not terminate")

    # Every created policy plus the bootstrap policy was returned exactly once.
    assert len(seen) == 6
    assert created <= set(seen)
    assert POLICYADMIN in seen
