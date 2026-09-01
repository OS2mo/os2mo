# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Address reads are guarded collection-based, not route-based.

It does not matter how an address is reached: every read resolves the same
addresses, the ones the caller may see per the collection's predicate (see
`mora.graphapi.policies`). Reaching for addresses is therefore never
forbidden; without the reader role the collection is simply empty.
"""

from collections.abc import Callable
from collections.abc import Iterator
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import true

from mora.db import OrganisationFunktionRegistrering
from mora.graphapi import policies
from mora.graphapi.policies import Policy
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

TOP_LEVEL = """
query {
    addresses {
        objects { uuid }
    }
}
"""

REDACTED = """
query {
    addresses(filter: {denied: REDACT}) {
        objects {
            uuid
            redacted
            reason
            current { value }
            validities { value }
        }
    }
}
"""

VALUES = """
query {
    addresses {
        objects {
            uuid
            redacted
            reason
            current { value }
        }
    }
}
"""

UUIDS_ONLY = """
query {
    addresses {
        objects {
            uuid
            redacted
            current { uuid }
        }
    }
}
"""

# The same request as VALUES, hiding the restricted field in a fragment
VALUES_VIA_FRAGMENT = """
query {
    addresses {
        objects {
            uuid
            redacted
            reason
            current { ... on Address { value } }
        }
    }
}
"""


@pytest.fixture
def set_address_policy() -> Iterator[Callable[[Policy], None]]:
    """Install an address policy for the duration of a test.

    Policies have no store of their own yet, so a test supplies one directly.
    """
    original = policies.POLICY_FOR["address"]

    def inner(policy: Policy) -> None:
        policies.POLICY_FOR["address"] = lambda token: policy

    yield inner
    policies.POLICY_FOR["address"] = original


NESTED = """
query {
    org_units {
        objects {
            objects {
                addresses { uuid }
            }
        }
    }
}
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
@pytest.mark.parametrize("roles", [set(), {"no_such_role"}])
async def test_addresses_empty_without_reader(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    roles: set[str],
) -> None:
    """Without the reader role the collection is empty, not forbidden."""
    set_auth(roles, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.errors is None
    assert response.data == {"addresses": {"objects": []}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_addresses_readable_via_query(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """The reader sees the address through the top-level collection."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.errors is None
    assert response.data
    assert {x["uuid"] for x in response.data["addresses"]["objects"]} == {
        str(org_unit_with_address)
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_addresses_readable_nested(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """The reader sees the same address hanging off its org-unit."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(NESTED)

    assert response.errors is None
    assert response.data
    assert {
        address["uuid"]
        for org_unit in response.data["org_units"]["objects"]
        for validity in org_unit["objects"]
        for address in validity["addresses"]
    } == {str(org_unit_with_address)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_redact_keeps_denied_addresses_as_bare_uuids(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """Asked to redact, a denied address stays, with its content withheld.

    This is what lets an integration tell "you may not read this" apart from
    "this was deleted": the UUID is still there.
    """
    set_auth(set(), uuid4())

    response = graphapi_post(REDACTED)

    assert response.errors is None
    assert response.data
    assert response.data["addresses"]["objects"] == [
        {
            "uuid": str(org_unit_with_address),
            "redacted": True,
            "reason": "not allowed to read the object",
            "current": None,
            "validities": [],
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_readable_addresses_are_not_redacted(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """An address the caller may read is not marked redacted."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(VALUES)

    assert response.errors is None
    assert response.data
    assert response.data["addresses"]["objects"] == [
        {
            "uuid": str(org_unit_with_address),
            "redacted": False,
            "reason": None,
            "current": {"value": "unit@example.org"},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_field_policy_withholds_only_the_denied_objects(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_address_policy: Callable[[Policy], None],
    two_addresses: tuple[UUID, UUID],
) -> None:
    """A field predicate limits which objects expose that field.

    Both addresses are readable, but `value` is granted on only one of them.
    Asking for it withholds the other's content entirely, naming the field;
    asking for something else returns both.
    """
    granted, denied = two_addresses
    set_address_policy(
        Policy(
            rows=true(),
            fields={
                "value": OrganisationFunktionRegistrering.organisationfunktion_id
                == granted
            },
        )
    )
    set_auth({"reader"}, uuid4())

    # Asking for the restricted field withholds it where it is not granted
    response = graphapi_post(VALUES)
    assert response.errors is None
    assert response.data
    by_uuid = {x["uuid"]: x for x in response.data["addresses"]["objects"]}
    assert by_uuid[str(granted)] == {
        "uuid": str(granted),
        "redacted": False,
        "reason": None,
        "current": {"value": "granted@example.org"},
    }
    assert by_uuid[str(denied)] == {
        "uuid": str(denied),
        "redacted": True,
        "reason": "not allowed to read: value",
        "current": None,
    }

    # Asking only for unrestricted fields returns both objects' content
    response = graphapi_post(UUIDS_ONLY)
    assert response.errors is None
    assert response.data
    assert {x["uuid"]: x["current"] for x in response.data["addresses"]["objects"]} == {
        str(granted): {"uuid": str(granted)},
        str(denied): {"uuid": str(denied)},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_field_policy_sees_through_fragments(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_address_policy: Callable[[Policy], None],
    two_addresses: tuple[UUID, UUID],
) -> None:
    """A restricted field is withheld even when asked for inside a fragment.

    A fragment is only a way of writing the selection down, so it must not
    let the caller sidestep the policy.
    """
    granted, denied = two_addresses
    set_address_policy(
        Policy(
            rows=true(),
            fields={
                "value": OrganisationFunktionRegistrering.organisationfunktion_id
                == granted
            },
        )
    )
    set_auth({"reader"}, uuid4())

    response = graphapi_post(VALUES_VIA_FRAGMENT)

    assert response.errors is None
    assert response.data
    by_uuid = {x["uuid"]: x for x in response.data["addresses"]["objects"]}
    assert by_uuid[str(denied)]["current"] is None
    assert by_uuid[str(denied)]["reason"] == "not allowed to read: value"
    assert by_uuid[str(granted)]["current"] == {"value": "granted@example.org"}
