# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the policies through GraphQL."""

from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from more_itertools import one

from mora.db import AsyncSession
from mora.db import Collection
from mora.db import Policy
from mora.db import PolicyReadRule
from mora.db import PolicyReadRuleField
from mora.db import PolicyWriteRule
from mora.graphapi.version import Version
from tests.conftest import BRUCE_UUID
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied

ReadPolicyPage = Callable[..., tuple[list[dict[str, Any]], str | None]]
ReadPolicies = Callable[..., list[dict[str, Any]]]

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
AUDITOR_UUID = "f1a00b99-399a-4a34-9e35-5873535a531c"


@pytest.fixture
def read_policy_page(graphapi_post: GraphAPIPost) -> ReadPolicyPage:
    """Read a page of policies, and the cursor of the next one."""

    def inner(
        variables: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        query = """
            query ReadPolicies($filter: PolicyFilter, $limit: int, $cursor: Cursor) {
                policies(filter: $filter, limit: $limit, cursor: $cursor) {
                    objects {
                        uuid
                        name
                        description
                        active
                        role
                        managed
                        read_rules { collection fields condition graphql_version }
                        write_rules { mutator condition graphql_version }
                    }
                    page_info { next_cursor }
                }
            }
        """
        response = graphapi_post(query=query, variables=variables)
        assert response.errors is None
        assert response.data is not None
        policies = response.data["policies"]
        return policies["objects"], policies["page_info"]["next_cursor"]

    return inner


@pytest.fixture
def read_policies(read_policy_page: ReadPolicyPage) -> ReadPolicies:
    """Read the policies, less the cursor."""

    def inner(variables: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        policies, _ = read_policy_page(variables)
        return policies

    return inner


@pytest.fixture
async def auditor(empty_db: AsyncSession) -> None:
    """A policy beside the seeded ones, switched off."""
    policy = Policy(
        pk=UUID(AUDITOR_UUID),
        name="Auditor",
        description="Reads the user key of the unit of the auditor",
        active=False,
        role="auditor",
        read_rules=[
            PolicyReadRule(
                collection=Collection.OrganisationUnit,
                condition='{"uuids": [token.uuid]}',
                graphql_version=Version.VERSION_29,
                fields=[PolicyReadRuleField(field="user_key")],
            )
        ],
        write_rules=[
            PolicyWriteRule(
                mutator="org_unit_update",
                condition="token.uuid != null",
                graphql_version=Version.VERSION_30,
            )
        ],
    )
    empty_db.add(policy)
    # A request opens its own session, so the rows must be committed to it
    await empty_db.commit()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_the_seeded_policy_is_read(read_policies: ReadPolicies) -> None:
    """The Reader policy the migrations seed comes back with its rules."""
    reader = one(read_policies({"filter": {"names": ["Reader"]}}))

    assert reader == {
        "uuid": READER_UUID,
        "name": "Reader",
        "description": "Read access to the fields of every collection",
        "active": True,
        "role": "reader",
        "managed": True,
        "read_rules": ANY,
        "write_rules": [],
    }
    read_rules = reader["read_rules"]
    assert {rule["collection"] for rule in read_rules} == {
        collection.value for collection in Collection
    }
    assert {rule["condition"] for rule in read_rules} == {"true"}
    assert {rule["graphql_version"] for rule in read_rules} == {"VERSION_30"}


@pytest.mark.integration_test
@pytest.mark.usefixtures("auditor")
async def test_a_policy_is_read_with_its_rules(read_policies: ReadPolicies) -> None:
    """A policy comes back as it is stored, rules and all."""
    policies = read_policies({"filter": {"names": ["Auditor"]}})
    assert policies == [
        {
            "uuid": AUDITOR_UUID,
            "name": "Auditor",
            "description": "Reads the user key of the unit of the auditor",
            "active": False,
            "role": "auditor",
            "managed": False,
            "read_rules": [
                {
                    "collection": "OrganisationUnit",
                    "fields": ["user_key"],
                    "condition": '{"uuids": [token.uuid]}',
                    "graphql_version": "VERSION_29",
                }
            ],
            "write_rules": [
                {
                    "mutator": "org_unit_update",
                    "condition": "token.uuid != null",
                    "graphql_version": "VERSION_30",
                }
            ],
        }
    ]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "filter,names",
    [
        # No filter, or an empty one, reads every policy
        (None, {"Reader", "Auditor"}),
        ({}, {"Reader", "Auditor"}),
        ({"uuids": []}, set()),
        ({"uuids": [READER_UUID]}, {"Reader"}),
        ({"uuids": [AUDITOR_UUID]}, {"Auditor"}),
        ({"uuids": [READER_UUID, AUDITOR_UUID]}, {"Reader", "Auditor"}),
        ({"names": []}, set()),
        ({"names": ["Reader"]}, {"Reader"}),
        ({"names": ["Auditor"]}, {"Auditor"}),
        ({"names": ["Reader", "Auditor"]}, {"Reader", "Auditor"}),
        ({"roles": []}, set()),
        ({"roles": ["reader"]}, {"Reader"}),
        ({"roles": ["auditor"]}, {"Auditor"}),
        ({"roles": ["reader", "auditor"]}, {"Reader", "Auditor"}),
        ({"active": True}, {"Reader"}),
        ({"active": False}, {"Auditor"}),
        # Filters intersect
        ({"roles": ["reader", "auditor"], "active": True}, {"Reader"}),
    ],
)
@pytest.mark.usefixtures("auditor")
async def test_policies_are_filtered(
    read_policies: ReadPolicies, filter: dict[str, Any] | None, names: set[str]
) -> None:
    """The filter picks the policies by uuid, name, role and whether they are active."""
    policies = read_policies({"filter": filter})
    assert {policy["name"] for policy in policies} == names


@pytest.mark.integration_test
@pytest.mark.usefixtures("auditor")
async def test_policies_are_paged(
    read_policies: ReadPolicies, read_policy_page: ReadPolicyPage
) -> None:
    """Paging walks every policy once, in the order of the unpaged read."""
    everything = read_policies()

    first, cursor = read_policy_page({"limit": 1})
    second, cursor = read_policy_page({"limit": 1, "cursor": cursor})

    assert first + second == everything
    assert cursor is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_may_not_read_the_policies(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    """Reading the policies takes an admin."""
    set_auth("reader", BRUCE_UUID)

    assert_denied(graphapi_post("query { policies { objects { name } } }"))
