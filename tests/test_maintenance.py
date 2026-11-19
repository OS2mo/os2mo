# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from more_itertools import one

from mora.maintenance import merge_duplicate_classes

from .conftest import AnotherTransaction
from .conftest import GraphAPIPost
from .test_events import declare_listener
from .test_events import fetch_event

CreateClass = Callable[[dict[str, Any]], UUID]


async def merge(
    another_transaction: AnotherTransaction, facet: UUID, user_key: str
) -> None:
    async with another_transaction() as (_, session):
        await merge_duplicate_classes(session, facet, user_key)


@pytest.fixture
def duplicate(create_class: CreateClass, org_unit_type_facet: UUID) -> UUID:
    """A duplicate of the `org_unit_type` fixture."""
    return create_class(
        {
            "user_key": "department",
            "name": "Department",
            "facet_uuid": str(org_unit_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )


def read_unit_types(graphapi_post: GraphAPIPost, org_unit: UUID) -> list[str]:
    response = graphapi_post(
        """
        query Read($uuid: UUID!) {
            org_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects { validities { unit_type_uuid } }
            }
        }
        """,
        {"uuid": str(org_unit)},
    )
    assert response.errors is None
    assert response.data
    validities = one(response.data["org_units"]["objects"])["validities"]
    return [validity["unit_type_uuid"] for validity in validities]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_merge_duplicate_classes(
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
    create_org_unit: Callable[..., UUID],
    org_unit_type_facet: UUID,
    org_unit_type: UUID,
    duplicate: UUID,
) -> None:
    org_unit = create_org_unit("unit", org_unit_type=duplicate)

    await merge(another_transaction, org_unit_type_facet, "department")

    response = graphapi_post(
        """
        query Read($facet: UUID!) {
            classes(filter: {facet: {uuids: [$facet]}}) { objects { uuid } }
        }
        """,
        {"facet": str(org_unit_type_facet)},
    )
    assert response.errors is None
    assert response.data
    assert response.data["classes"]["objects"] == [{"uuid": str(org_unit_type)}]
    assert read_unit_types(graphapi_post, org_unit) == [str(org_unit_type)]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_merge_duplicate_classes_rewrites_history(
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
    create_org_unit: Callable[..., UUID],
    update_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type_facet: UUID,
    org_unit_type: UUID,
    duplicate: UUID,
) -> None:
    """Past validities point to the original, not to a deleted class."""
    org_unit = create_org_unit("unit", org_unit_type=duplicate)
    update_org_unit(
        {
            "uuid": str(org_unit),
            "org_unit_type": str(org_unit_type),
            "validity": {"from": "2010-01-01"},
        }
    )

    await merge(another_transaction, org_unit_type_facet, "department")

    # Both validities now have the same type, so they are read as one
    assert read_unit_types(graphapi_post, org_unit) == [str(org_unit_type)]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_type")
async def test_merge_duplicate_classes_emits_events(
    graphapi_post: GraphAPIPost,
    admin_client: TestClient,
    another_transaction: AnotherTransaction,
    create_org_unit: Callable[..., UUID],
    org_unit_type_facet: UUID,
    duplicate: UUID,
) -> None:
    """The event generator emits events for objects with changed references."""
    org_unit = create_org_unit("unit", org_unit_type=duplicate)
    # Emit the creation events before listening
    admin_client.post("/testing/amqp/emit")
    listener = declare_listener(graphapi_post, "mo", "listener", "org_unit")

    await merge(another_transaction, org_unit_type_facet, "department")
    admin_client.post("/testing/amqp/emit")

    event = fetch_event(graphapi_post, listener)
    assert event is not None
    assert event["subject"] == str(org_unit)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_merge_duplicate_roles(
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
    create_class: CreateClass,
    create_rolebinding_rule: Callable[[dict[str, Any]], UUID],
    role_facet: UUID,
    itsystem: UUID,
    role: UUID,
) -> None:
    duplicate_role = create_class(
        {
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem),
            "user_key": "read",
            "name": "Read",
            "validity": {"from": "1970-01-01"},
        }
    )
    rule = create_rolebinding_rule(
        {"name": "rule", "role": str(duplicate_role), "expression": "true"}
    )

    await merge(another_transaction, role_facet, "read")

    response = graphapi_post(
        """
        query Read($uuid: UUID!) {
            rolebinding_rules(filter: {uuids: [$uuid]}) {
                objects { current { role { uuid } } }
            }
        }
        """,
        {"uuid": str(rule)},
    )
    assert response.errors is None
    assert response.data
    assert response.data["rolebinding_rules"]["objects"] == [
        {"current": {"role": {"uuid": str(role)}}}
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_merge_refuses_self_reference(
    another_transaction: AnotherTransaction,
    update_class: Callable[[dict[str, Any]], UUID],
    org_unit_type_facet: UUID,
    org_unit_type: UUID,
    duplicate: UUID,
) -> None:
    """The original cannot become its own parent."""
    update_class(
        {
            "uuid": str(org_unit_type),
            "user_key": "department",
            "name": "Department",
            "facet_uuid": str(org_unit_type_facet),
            "parent_uuid": str(duplicate),
            "validity": {"from": "1970-01-01"},
        }
    )

    with pytest.raises(ValueError, match="references a duplicate"):
        await merge(another_transaction, org_unit_type_facet, "department")
