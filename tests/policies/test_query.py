# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the `policies` query and `me.policies`."""

from collections.abc import Callable

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.policies.conftest import DEFAULT_POLICIES
from tests.policies.conftest import CreatePolicy
from tests.policies.helpers import UnorderedList
from tests.policies.helpers import assert_access


@pytest.fixture
def read_policy_names(graphapi_post: GraphAPIPost) -> Callable[[dict | None], set[str]]:
    """The names of the policies a filter selects."""

    def inner(filter: dict | None = None) -> set[str]:
        response = graphapi_post(
            """
          query FilterPolicies($filter: PolicyFilter) {
            policies(filter: $filter) {
              objects {
                name
              }
            }
          }
        """,
            variables={"filter": filter},
        )
        assert response.errors is None
        return {obj["name"] for obj in response.data["policies"]["objects"]}

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policies_reads_the_default_policies(
    read_policy_names: Callable[[dict | None], set[str]],
) -> None:
    """The query returns the migration-seeded policies."""
    assert read_policy_names() == DEFAULT_POLICIES


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "query",
    [
        "query { policies { objects { name } } }",
        "query { me { policies { name } } }",
    ],
)
@pytest.mark.parametrize(
    ("role", "granted"),
    [
        ("nobody", False),
        ("read_policy", True),
        ("declare_policy", False),
    ],
)
async def test_policies_requires_a_grant(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, query: str, role: str, granted: bool
) -> None:
    """Neither entry point is public: both take the read_policy grant."""
    set_auth(role=role)
    assert_access(graphapi_post(query), granted)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: everything returned, active and inactive alike
        (None, {"reader_on", "reader_off", "editor_on"} | DEFAULT_POLICIES),
        ({}, {"reader_on", "reader_off", "editor_on"} | DEFAULT_POLICIES),
        # By activation state
        ({"active": True}, {"reader_on", "editor_on"} | DEFAULT_POLICIES),
        ({"active": False}, {"reader_off"}),
        # By name
        ({"names": ["reader_on"]}, {"reader_on"}),
        ({"names": ["reader_on", "editor_on"]}, {"reader_on", "editor_on"}),
        ({"names": []}, set()),
        # By actor roles. The all-actor defaults match every role-based
        # filter; Owner matches only its own role
        (
            {"actor": {"roles": ["reader"]}},
            {"reader_on", "reader_off"} | DEFAULT_POLICIES - {"Owner"},
        ),
        (
            {"actor": {"roles": ["editor"]}},
            {"editor_on"} | DEFAULT_POLICIES - {"Owner"},
        ),
        ({"actor": {"roles": ["owner"]}}, DEFAULT_POLICIES),
        # Several roles match a policy bound to any of them
        (
            {"actor": {"roles": ["reader", "editor"]}},
            {"reader_on", "reader_off", "editor_on"} | DEFAULT_POLICIES - {"Owner"},
        ),
        # An empty role list matches no role-bound policy, but still matches
        # the all-actor ones
        ({"actor": {"roles": []}}, DEFAULT_POLICIES - {"Owner"}),
        # No roles provided means "has any actor"
        ({"actor": {}}, {"reader_on", "reader_off", "editor_on"} | DEFAULT_POLICIES),
        # Several dimensions select their intersection
        (
            {"active": True, "actor": {"roles": ["reader"]}},
            {"reader_on"} | DEFAULT_POLICIES - {"Owner"},
        ),
        ({"active": False, "actor": {"roles": ["reader"]}}, {"reader_off"}),
        ({"active": False, "actor": {"roles": ["editor"]}}, set()),
    ],
)
async def test_policies_filter(
    create_policy: CreatePolicy,
    read_policy_names: Callable[[dict | None], set[str]],
    filter: dict | None,
    expected: set[str],
) -> None:
    """Each filter dimension, and their conjunction, selects the expected policies."""
    # The default policies cover the active all-actor case; the rest is created
    await create_policy("reader_on", actors=[("role", "reader")], rules=[])
    await create_policy(
        "reader_off", actors=[("role", "reader")], rules=[], active=False
    )
    await create_policy("editor_on", actors=[("role", "editor")], rules=[])

    assert read_policy_names(filter) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policies_filter_by_uuid(
    graphapi_post: GraphAPIPost,
    create_policy: CreatePolicy,
    read_policy_names: Callable[[dict | None], set[str]],
) -> None:
    await create_policy("wanted", actors=[("role", "x")], rules=[])

    response = graphapi_post(
        """
      query ReadWanted($filter: PolicyFilter) {
        policies(filter: $filter) {
          objects {
            uuid
          }
        }
      }
    """,
        variables={"filter": {"names": ["wanted"]}},
    )
    assert response.errors is None
    wanted = one(response.data["policies"]["objects"])["uuid"]

    await create_policy("other", actors=[("role", "y")], rules=[])

    assert read_policy_names({"uuids": [wanted]}) == {"wanted"}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policies_reads_nested_actors_and_rules(
    graphapi_post: GraphAPIPost, create_policy: CreatePolicy
) -> None:
    await create_policy(
        "nested",
        actors=[("role", "reader")],
        rules=[("Query", "org_units"), ("Mutation", "employee_update", "true", "")],
    )

    response = graphapi_post(
        """
      query ReadNested($filter: PolicyFilter) {
        policies(filter: $filter) {
          objects {
            actors {
              kind
              value
            }
            rules {
              type
              field
              condition
              filter
            }
          }
        }
      }
    """,
        variables={"filter": {"names": ["nested"]}},
    )
    assert response.errors is None
    policy = one(response.data["policies"]["objects"])

    assert policy == {
        "actors": UnorderedList([{"kind": "role", "value": "reader"}]),
        "rules": UnorderedList(
            [
                {
                    "type": "Query",
                    "field": "org_units",
                    "condition": "",
                    "filter": "",
                },
                {
                    "type": "Mutation",
                    "field": "employee_update",
                    "condition": "true",
                    "filter": "",
                },
            ]
        ),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_policies_pagination(graphapi_post: GraphAPIPost) -> None:
    """Paging by two walks every policy in order, each exactly once."""

    def read(limit: int | None, cursor: str | None) -> tuple[list[dict], str | None]:
        response = graphapi_post(
            """
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
        """,
            variables={"limit": limit, "cursor": cursor},
        )
        assert response.errors is None
        page = response.data["policies"]
        return page["objects"], page["page_info"]["next_cursor"]

    # The unpaginated read fixes the expected order and elements
    everything, cursor = read(None, None)
    assert {obj["name"] for obj in everything} == DEFAULT_POLICIES
    assert cursor is None

    # The paginated walk reproduces it two at a time, in three pages
    first, cursor = read(2, None)
    assert first == everything[0:2]
    assert cursor is not None

    second, cursor = read(2, cursor)
    assert second == everything[2:4]
    assert cursor is not None

    third, cursor = read(2, cursor)
    assert third == everything[4:]
    assert cursor is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_me_policies_is_seeded_from_the_caller(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """`me.policies` returns only the policies applicable to the caller."""

    def read_my_policy_names() -> set[str]:
        response = graphapi_post(
            """
          query ReadMyPolicies {
            me {
              policies {
                name
              }
            }
          }
        """
        )
        assert response.errors is None
        return {obj["name"] for obj in response.data["me"]["policies"]}

    set_auth(role="read_policy")
    # Owner is bound to the owner role, which the caller lacks
    assert read_my_policy_names() == DEFAULT_POLICIES - {"Owner"}

    set_auth(role="owner")
    # The owner role holds every read grant, and its own policy too
    assert read_my_policy_names() == DEFAULT_POLICIES
