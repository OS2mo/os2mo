# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the policies through GraphQL."""

from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID
from uuid import uuid4

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
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted

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


TryDeclarePolicy = Callable[[str, dict[str, Any] | None], GQLResponse]
DeclarePolicy = Callable[[str, dict[str, Any]], dict[str, Any]]


@pytest.fixture
def try_declare_policy(graphapi_post: GraphAPIPost) -> TryDeclarePolicy:
    """Declare the state of a policy, and return the response unchecked."""

    def inner(uuid: str, state: dict[str, Any] | None) -> GQLResponse:
        query = """
            mutation Declare($uuid: UUID!, $state: PolicyStateInput) {
                policy_declare(uuid: $uuid, state: $state) {
                    uuid
                    name
                    description
                    active
                    role
                    managed
                    read_rules { collection fields condition graphql_version }
                    write_rules { mutator condition graphql_version }
                }
            }
        """
        return graphapi_post(query=query, variables={"uuid": uuid, "state": state})

    return inner


@pytest.fixture
def declare_policy(try_declare_policy: TryDeclarePolicy) -> DeclarePolicy:
    """Declare the state of a policy, and return the policy as it was declared."""

    def inner(uuid: str, state: dict[str, Any]) -> dict[str, Any]:
        response = try_declare_policy(uuid, state)
        assert response.errors is None
        assert response.data is not None
        return response.data["policy_declare"]

    return inner


# The state of a policy as it is declared
UNIT_AUDITOR = {
    "name": "Unit Auditor",
    "role": "unit_auditor",
    "description": "Audits the unit of the auditor",
    "active": True,
    "read_rules": [
        {
            "collection": "OrganisationUnit",
            "fields": ["user_key"],
            "condition": '{"uuids": [token.uuid]}',
            "graphql_version": "VERSION_30",
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_declared_policy_is_read_back(
    declare_policy: DeclarePolicy, read_policies: ReadPolicies
) -> None:
    """Declaring a policy stores it as it was declared."""
    uuid = str(uuid4())
    policy = declare_policy(uuid, UNIT_AUDITOR)

    assert policy == {
        "uuid": uuid,
        "name": "Unit Auditor",
        "role": "unit_auditor",
        "description": "Audits the unit of the auditor",
        "active": True,
        "managed": False,
        "read_rules": [
            {
                "collection": "OrganisationUnit",
                "fields": ["user_key"],
                "condition": '{"uuids": [token.uuid]}',
                "graphql_version": "VERSION_30",
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
    policies = read_policies({"filter": {"uuids": [uuid]}})
    assert policies == [policy]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_policy_declared_again_is_left_as_it_was(
    declare_policy: DeclarePolicy, read_policies: ReadPolicies
) -> None:
    """Declaring the same policy twice changes nothing the second time."""
    uuid = str(uuid4())
    first = declare_policy(uuid, UNIT_AUDITOR)
    again = declare_policy(uuid, UNIT_AUDITOR)

    assert again == first
    policies = read_policies({"filter": {"uuids": [uuid]}})
    assert policies == [first]


@pytest.mark.integration_test
@pytest.mark.usefixtures("auditor")
async def test_a_policy_declared_anew_is_made_to_match(
    declare_policy: DeclarePolicy, read_policies: ReadPolicies
) -> None:
    """Declaring a policy anew replaces it, name, rules and all."""
    policy = declare_policy(
        AUDITOR_UUID,
        {
            "name": "Class Auditor",
            "role": "class_auditor",
            "description": "Audits every class",
            "active": True,
            "read_rules": [
                {
                    "collection": "Class",
                    "fields": ["name"],
                    "condition": "true",
                    "graphql_version": "VERSION_30",
                }
            ],
            "write_rules": [],
        },
    )

    assert policy == {
        "uuid": AUDITOR_UUID,
        "name": "Class Auditor",
        "role": "class_auditor",
        "description": "Audits every class",
        "active": True,
        "managed": False,
        "read_rules": [
            {
                "collection": "Class",
                "fields": ["name"],
                "condition": "true",
                "graphql_version": "VERSION_30",
            }
        ],
        "write_rules": [],
    }
    policies = read_policies({"filter": {"uuids": [AUDITOR_UUID]}})
    assert policies == [policy]


@pytest.mark.integration_test
@pytest.mark.usefixtures("auditor")
async def test_a_policy_cannot_take_the_name_of_another(
    try_declare_policy: TryDeclarePolicy,
    declare_policy: DeclarePolicy,
    read_policies: ReadPolicies,
) -> None:
    """Names are unique, so a policy cannot be renamed to that of another."""
    uuid = str(uuid4())
    before = declare_policy(uuid, UNIT_AUDITOR)

    response = try_declare_policy(uuid, {**UNIT_AUDITOR, "name": "Auditor"})

    assert response.errors is not None
    assert one(response.errors)["message"] == "There is another policy named 'Auditor'."
    assert read_policies({"filter": {"uuids": [uuid]}}) == [before]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_rule_is_written_in_the_version_it_is_declared_in(
    declare_policy: DeclarePolicy,
) -> None:
    """Each rule takes the GraphQL version declared for it, not that of the endpoint."""
    policy = declare_policy(
        str(uuid4()),
        {
            "name": "Unit Auditor",
            "role": "unit_auditor",
            "read_rules": [
                {
                    "collection": "OrganisationUnit",
                    "fields": ["user_key"],
                    "graphql_version": "VERSION_29",
                }
            ],
            "write_rules": [
                {"mutator": "org_unit_update", "graphql_version": "VERSION_28"}
            ],
        },
    )

    assert one(policy["read_rules"])["graphql_version"] == "VERSION_29"
    assert one(policy["write_rules"])["graphql_version"] == "VERSION_28"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_read_rule_is_unconditional_by_default(
    declare_policy: DeclarePolicy, read_policies: ReadPolicies
) -> None:
    """A read rule declared without a condition grants its fields on every object."""
    uuid = str(uuid4())
    declare_policy(
        uuid,
        {
            "name": "Address Auditor",
            "role": "address_auditor",
            "read_rules": [
                {
                    "collection": "Address",
                    "fields": ["value"],
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )

    policy = one(read_policies({"filter": {"uuids": [uuid]}}))
    assert policy["read_rules"] == [
        {
            "collection": "Address",
            "fields": ["value"],
            "condition": "true",
            "graphql_version": "VERSION_30",
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_read_rule_naming_a_field_twice_is_refused(
    try_declare_policy: TryDeclarePolicy, read_policies: ReadPolicies
) -> None:
    """A read rule names each of its fields once, or nothing is declared."""
    uuid = str(uuid4())
    read_rule = {
        "collection": "Address",
        "fields": ["uuid", "value", "uuid"],
        "graphql_version": "VERSION_30",
    }

    response = try_declare_policy(uuid, {**UNIT_AUDITOR, "read_rules": [read_rule]})

    assert response.errors is not None
    assert (
        one(response.errors)["message"]
        == "A read rule cannot name a field more than once."
    )
    assert read_policies({"filter": {"uuids": [uuid]}}) == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_declared_policy_grants_its_rules(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, declare_policy: DeclarePolicy
) -> None:
    """The rules of a declared policy are in force as soon as it is declared."""
    namespace_declare = """
        mutation { event_namespace_declare(input: {name: "audits"}) { name } }
    """
    set_auth({"reader", "event_admin"}, BRUCE_UUID)
    assert_denied(graphapi_post(namespace_declare))

    set_auth("admin", BRUCE_UUID)
    declare_policy(
        str(uuid4()),
        {
            "name": "Event Admin",
            "role": "event_admin",
            "write_rules": [
                {"mutator": "event_namespace_declare", "graphql_version": "VERSION_30"}
            ],
        },
    )

    set_auth({"reader", "event_admin"}, BRUCE_UUID)
    assert_granted(graphapi_post(namespace_declare))


@pytest.mark.integration_test
@pytest.mark.parametrize("state", [UNIT_AUDITOR, None])
@pytest.mark.usefixtures("empty_db")
async def test_a_managed_policy_cannot_be_modified(
    try_declare_policy: TryDeclarePolicy,
    read_policies: ReadPolicies,
    state: dict[str, Any] | None,
) -> None:
    """A policy MO manages is neither replaced nor deleted, but left as it was."""
    before = read_policies({"filter": {"names": ["Reader"]}})

    response = try_declare_policy(one(before)["uuid"], state)

    assert response.errors is not None
    assert one(response.errors)["message"] == "A managed policy cannot be modified."
    assert read_policies({"filter": {"names": ["Reader"]}}) == before


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_may_not_declare_a_policy(
    set_auth: SetAuth, try_declare_policy: TryDeclarePolicy
) -> None:
    """Declaring a policy takes an admin."""
    set_auth("reader", BRUCE_UUID)

    assert_denied(try_declare_policy(str(uuid4()), UNIT_AUDITOR))


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "rules,error",
    [
        (
            {
                "read_rules": [
                    {
                        "collection": "Address",
                        "fields": ["uuid"],
                        "condition": "{",
                        "graphql_version": "VERSION_30",
                    }
                ]
            },
            "condition '{' does not compile: ",
        ),
        (
            {
                "write_rules": [
                    {
                        "mutator": "address_create",
                        "condition": "tokn.roles",
                        "graphql_version": "VERSION_30",
                    }
                ]
            },
            "condition 'tokn.roles' does not compile: ",
        ),
        (
            {
                "write_rules": [
                    {
                        "mutator": "address_create",
                        "condition": "",
                        "graphql_version": "VERSION_30",
                    }
                ]
            },
            "condition '' does not compile: ",
        ),
    ],
)
@pytest.mark.usefixtures("empty_db")
async def test_a_condition_which_does_not_compile_is_refused(
    try_declare_policy: TryDeclarePolicy,
    read_policies: ReadPolicies,
    rules: dict[str, Any],
    error: str,
) -> None:
    """A condition which does not compile is refused, and nothing is declared."""
    uuid = str(uuid4())
    state = {
        "name": "Unit Auditor",
        "role": "unit_auditor",
        **rules,
    }

    response = try_declare_policy(uuid, state)

    assert response.errors is not None
    assert error in one(response.errors)["message"]
    policies = read_policies({"filter": {"uuids": [uuid]}})
    assert policies == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_deleted_policy_is_gone(
    try_declare_policy: TryDeclarePolicy,
    declare_policy: DeclarePolicy,
    read_policies: ReadPolicies,
) -> None:
    """Declaring no state deletes a policy along with its rules, and nothing else."""
    before = read_policies()
    uuid = str(uuid4())
    declare_policy(uuid, UNIT_AUDITOR)

    response = try_declare_policy(uuid, None)

    assert response.errors is None
    assert response.data == {"policy_declare": None}
    after = read_policies()
    assert after == before


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_deleted_policy_grants_nothing(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    try_declare_policy: TryDeclarePolicy,
    declare_policy: DeclarePolicy,
) -> None:
    """The rules of a deleted policy are out of force as soon as it is deleted."""
    namespace_declare = """
        mutation { event_namespace_declare(input: {name: "audits"}) { name } }
    """
    uuid = str(uuid4())
    declare_policy(
        uuid,
        {
            "name": "Event Admin",
            "role": "event_admin",
            "write_rules": [
                {"mutator": "event_namespace_declare", "graphql_version": "VERSION_30"}
            ],
        },
    )
    set_auth({"reader", "event_admin"}, BRUCE_UUID)
    assert_granted(graphapi_post(namespace_declare))

    set_auth("admin", BRUCE_UUID)
    assert try_declare_policy(uuid, None).errors is None

    set_auth({"reader", "event_admin"}, BRUCE_UUID)
    assert_denied(graphapi_post(namespace_declare))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_deleting_a_policy_which_does_not_exist_does_nothing(
    try_declare_policy: TryDeclarePolicy,
) -> None:
    """Deleting a policy nobody declared succeeds, having nothing to delete."""
    response = try_declare_policy(str(uuid4()), None)

    assert response.errors is None
    assert response.data == {"policy_declare": None}
