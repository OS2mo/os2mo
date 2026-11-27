# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from tests.conftest import GQLResponse
from tests.conftest import SetAuth

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the related_unit data model."""
    query = """
        query {
            related_units {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        org_unit_response { uuid }
                        related_org_unit_response { uuid }
                        type
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


RELATED_UNIT_FIELDS = """
    uuid
    user_key
    org_unit_response { uuid current { user_key } }
    related_org_unit_response { uuid current { user_key } }
    validity { from to }
"""


@pytest.fixture
def create_related_unit(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], GQLResponse]:
    def inner(input: dict[str, Any]) -> GQLResponse:
        mutation = """
            mutation CreateRelatedUnit($input: RelatedUnitCreateInput!) {
                related_unit_create(input: $input) {
                    uuid
                }
            }
        """
        return graphapi_post(mutation, {"input": jsonable_encoder(input)})

    return inner


@pytest.fixture
def read_related_unit(
    graphapi_post: GraphAPIPost,
) -> Callable[..., list[dict[str, Any]]]:
    def inner(uuid: UUID, from_date: str | None = None) -> list[dict[str, Any]]:
        query = f"""
            query ReadRelatedUnit($uuid: UUID!, $from_date: DateTime) {{
                related_units(filter: {{uuids: [$uuid], from_date: $from_date, to_date: null}}) {{
                    objects {{
                        validities {{
                            {RELATED_UNIT_FIELDS}
                        }}
                    }}
                }}
            }}
        """
        response = graphapi_post(query, {"uuid": str(uuid), "from_date": from_date})
        assert response.errors is None
        return one(response.data["related_units"]["objects"])["validities"]

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_create(
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
    read_related_unit: Callable[..., list[dict[str, Any]]],
) -> None:
    units = [
        create_org_unit(
            f"unit{i}", uuid=UUID(f"00000000-0000-0000-0000-00000000000{i}")
        )
        for i in range(4)
    ]

    # LoRa returns the units in UUID order, so relate them in both orders
    for unit, related_unit in ((units[0], units[3]), (units[2], units[1])):
        response = create_related_unit(
            {
                "org_unit": str(unit),
                "related_org_unit": str(related_unit),
                "validity": {"from": "2020-01-01"},
            }
        )
        assert response.errors is None
        uuid = UUID(response.data["related_unit_create"]["uuid"])

        unit_key = f"unit{units.index(unit)}"
        related_unit_key = f"unit{units.index(related_unit)}"
        assert read_related_unit(uuid) == [
            {
                "uuid": str(uuid),
                "user_key": f"{unit_key} <-> {related_unit_key}",
                "org_unit_response": {
                    "uuid": str(unit),
                    "current": {"user_key": unit_key},
                },
                "related_org_unit_response": {
                    "uuid": str(related_unit),
                    "current": {"user_key": related_unit_key},
                },
                "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
            }
        ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_create_with_user_key_and_uuid(
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
    read_related_unit: Callable[..., list[dict[str, Any]]],
) -> None:
    uuid = uuid4()
    response = create_related_unit(
        {
            "uuid": str(uuid),
            "user_key": "my relation",
            "org_unit": str(create_org_unit("a")),
            "related_org_unit": str(create_org_unit("b")),
            "validity": {"from": "2020-01-01", "to": "2030-12-31"},
        }
    )
    assert response.errors is None
    assert response.data["related_unit_create"]["uuid"] == str(uuid)

    validity = one(read_related_unit(uuid))
    assert validity["user_key"] == "my relation"
    assert validity["validity"] == {
        "from": "2020-01-01T00:00:00+01:00",
        "to": "2030-12-31T00:00:00+01:00",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_create_related_to_self(
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
) -> None:
    unit = create_org_unit("a")
    response = create_related_unit(
        {
            "org_unit": str(unit),
            "related_org_unit": str(unit),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert response.errors is not None
    assert one(response.errors)["extensions"]["error_context"]["error_key"] == (
        "E_RELATED_TO_SELF"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_create_outside_unit_validity(
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
) -> None:
    response = create_related_unit(
        {
            "org_unit": str(create_org_unit("a")),
            "related_org_unit": str(
                create_org_unit("b", validity={"from": "2025-01-01"})
            ),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert response.errors is not None
    assert one(response.errors)["extensions"]["error_context"]["error_key"] == (
        "V_DATE_OUTSIDE_ORG_UNIT_RANGE"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_update_user_key(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
    read_related_unit: Callable[..., list[dict[str, Any]]],
) -> None:
    a = create_org_unit("a")
    b = create_org_unit("b")
    response = create_related_unit(
        {
            "org_unit": str(a),
            "related_org_unit": str(b),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert response.errors is None
    uuid = UUID(response.data["related_unit_create"]["uuid"])

    mutation = """
        mutation UpdateRelatedUnit($input: RelatedUnitUpdateInput!) {
            related_unit_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        mutation,
        {
            "input": {
                "uuid": str(uuid),
                "user_key": "renamed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None

    validity = one(read_related_unit(uuid, from_date=None))
    assert validity["user_key"] == "renamed"
    assert validity["org_unit_response"]["uuid"] == str(a)
    assert validity["related_org_unit_response"]["uuid"] == str(b)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_terminate(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
    read_related_unit: Callable[..., list[dict[str, Any]]],
) -> None:
    response = create_related_unit(
        {
            "org_unit": str(create_org_unit("a")),
            "related_org_unit": str(create_org_unit("b")),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert response.errors is None
    uuid = UUID(response.data["related_unit_create"]["uuid"])

    mutation = """
        mutation TerminateRelatedUnit($input: RelatedUnitTerminateInput!) {
            related_unit_terminate(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        mutation, {"input": {"uuid": str(uuid), "to": "2025-12-31"}}
    )
    assert response.errors is None
    assert response.data["related_unit_terminate"]["uuid"] == str(uuid)

    validity = one(read_related_unit(uuid, from_date=None))
    assert validity["validity"] == {
        "from": "2020-01-01T00:00:00+01:00",
        "to": "2025-12-31T00:00:00+01:00",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("swap", [False, True])
async def test_related_unit_create_duplicate(
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
    swap: bool,
) -> None:
    """Units cannot be related more than once at a time, in either direction."""
    a = create_org_unit("a")
    b = create_org_unit("b")
    response = create_related_unit(
        {
            "org_unit": str(a),
            "related_org_unit": str(b),
            "validity": {"from": "2020-01-01", "to": "2020-12-31"},
        }
    )
    assert response.errors is None

    org_unit, related_org_unit = (b, a) if swap else (a, b)
    response = create_related_unit(
        {
            "org_unit": str(org_unit),
            "related_org_unit": str(related_org_unit),
            "validity": {"from": "2020-06-01"},
        }
    )
    assert response.errors is not None
    assert one(response.errors)["extensions"]["error_context"]["error_key"] == (
        "V_DUPLICATED_RELATED_UNIT"
    )

    # Relating them again once the first relation has ended is fine
    response = create_related_unit(
        {
            "org_unit": str(org_unit),
            "related_org_unit": str(related_org_unit),
            "validity": {"from": "2021-01-01"},
        }
    )
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_reads_the_units_of_a_related_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
) -> None:
    """The Reader policy grants the units of related units."""
    a = create_org_unit("a")
    b = create_org_unit("b")
    response = create_related_unit(
        {
            "org_unit": str(a),
            "related_org_unit": str(b),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert response.errors is None

    set_auth({"reader"}, uuid4())
    response = graphapi_post(
        """
        query {
            related_units {
                objects {
                    current {
                        org_unit_response { uuid }
                        related_org_unit_response { uuid }
                    }
                }
            }
        }
        """
    )
    assert response.errors is None
    assert one(response.data["related_units"]["objects"])["current"] == {
        "org_unit_response": {"uuid": str(a)},
        "related_org_unit_response": {"uuid": str(b)},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("field", ["org_unit", "related_org_unit"])
async def test_related_unit_update_cannot_change_units(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    field: str,
) -> None:
    """A relation between other units is another relation.

    To relate other units, terminate the relation and create another.
    """
    response = graphapi_post(
        """
        mutation UpdateRelatedUnit($input: RelatedUnitUpdateInput!) {
            related_unit_update(input: $input) { uuid }
        }
        """,
        {
            "input": {
                "uuid": str(uuid4()),
                field: str(create_org_unit("other")),
                "validity": {"from": "2022-01-01"},
            }
        },
    )
    assert response.errors is not None
    assert (
        f"Field '{field}' is not defined by type 'RelatedUnitUpdateInput'"
        in (one(response.errors)["message"])
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_update_into_duplicate(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_related_unit: Callable[[dict[str, Any]], GQLResponse],
) -> None:
    """A relation cannot be extended into another relation of the same units."""
    a = create_org_unit("a")
    b = create_org_unit("b")
    response = create_related_unit(
        {
            "org_unit": str(a),
            "related_org_unit": str(b),
            "validity": {"from": "2020-01-01", "to": "2020-12-31"},
        }
    )
    assert response.errors is None
    uuid = response.data["related_unit_create"]["uuid"]
    response = create_related_unit(
        {
            "org_unit": str(b),
            "related_org_unit": str(a),
            "validity": {"from": "2022-01-01"},
        }
    )
    assert response.errors is None

    def extend(to: str | None) -> GQLResponse:
        return graphapi_post(
            """
            mutation UpdateRelatedUnit($input: RelatedUnitUpdateInput!) {
                related_unit_update(input: $input) { uuid }
            }
            """,
            {"input": {"uuid": uuid, "validity": {"from": "2020-01-01", "to": to}}},
        )

    response = extend(None)
    assert response.errors is not None
    assert one(response.errors)["extensions"]["error_context"]["error_key"] == (
        "V_DUPLICATED_RELATED_UNIT"
    )
    # Extending it until the other relation starts is fine
    assert extend("2021-12-31").errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_related_unit_update_not_found(graphapi_post: GraphAPIPost) -> None:
    """Updating a related unit which does not exist is rejected."""
    response = graphapi_post(
        """
        mutation UpdateRelatedUnit($input: RelatedUnitUpdateInput!) {
            related_unit_update(input: $input) { uuid }
        }
        """,
        {
            "input": {
                "uuid": str(uuid4()),
                "user_key": "renamed",
                "validity": {"from": "2022-01-01"},
            }
        },
    )
    assert response.errors is not None
    assert one(response.errors)["extensions"]["error_context"]["error_key"] == (
        "E_NOT_FOUND"
    )
