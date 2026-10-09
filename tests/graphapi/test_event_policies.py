# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of event listeners are guarded by read policies rather than by role."""

from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from mora.db import Collection
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules

DENIED = "No policy approved the access"


def _failures(response: Any) -> set[tuple[str, tuple[str | int, ...]]]:
    """The errors of *response*, as (message, path) pairs."""
    return {(error["message"], tuple(error["path"])) for error in response.errors}


@pytest.fixture
def listener(graphapi_post: GraphAPIPost) -> UUID:
    """A listener in a namespace of its own, declared by an admin."""
    response = graphapi_post(
        """
        mutation {
          event_namespace_declare(input: { name: "ns", public: false }) { name }
          event_listener_declare(
            input: { namespace: "ns", user_key: "listener", routing_key: "key" }
          ) { uuid }
        }
        """
    )
    assert response.errors is None
    assert response.data
    return UUID(response.data["event_listener_declare"]["uuid"])


LISTENERS = """
query {
  event_listeners(filter: { namespaces: { names: ["ns"] } }) {
    objects { uuid user_key routing_key }
  }
}
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_reads_the_fields_of_a_listener(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, listener: UUID
) -> None:
    """The seeded Reader policy grants a reader what the role used to."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(LISTENERS)

    assert response.errors is None
    assert response.data == {
        "event_listeners": {
            "objects": [
                {"uuid": str(listener), "user_key": "listener", "routing_key": "key"}
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_listener_field_no_rule_grants_is_denied(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    listener: UUID,
) -> None:
    """A field of a listener no rule grants is denied where it is read.

    The listeners are not nullable, so the denial nulls the whole response.
    """
    await set_rules("reader", Collection.Listener, {"uuid", "user_key"})
    set_auth({"reader"}, uuid4())

    response = graphapi_post(LISTENERS)

    assert response.data is None
    assert _failures(response) == {
        (DENIED, ("event_listeners", "objects", 0, "routing_key"))
    }
