# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import collapse
from more_itertools import first

from ..conftest import GraphAPIPost

# Every organisation function collection that batches its lookups, paired with
# each relation it batches on.
RELATIONS = [
    ("addresses", "AddressFilter", "employee"),
    ("addresses", "AddressFilter", "org_unit"),
    ("associations", "AssociationFilter", "employee"),
    ("associations", "AssociationFilter", "org_unit"),
    ("engagements", "EngagementFilter", "employee"),
    ("engagements", "EngagementFilter", "org_unit"),
    ("itusers", "ITUserFilter", "employee"),
    ("itusers", "ITUserFilter", "org_unit"),
    ("kles", "KLEFilter", "org_unit"),
    ("leaves", "LeaveFilter", "employee"),
    ("leaves", "LeaveFilter", "org_unit"),
    ("managers", "ManagerFilter", "employee"),
    ("managers", "ManagerFilter", "org_unit"),
    ("owners", "OwnerFilter", "employee"),
    ("owners", "OwnerFilter", "org_unit"),
    ("related_units", "RelatedUnitFilter", "org_unit"),
    ("rolebindings", "RoleBindingFilter", "org_unit"),
]


def find_related_uuid(
    graphapi_post: GraphAPIPost, collection: str, relation: str
) -> str | None:
    """A UUID of a `relation` that the fixture has `collection` objects for."""
    # Objects related to one object expose its UUID. Objects related to several,
    # such as related units, expose a list of UUIDs instead.
    for field in (f"{relation}_uuid", f"{relation}_uuids"):
        response = graphapi_post(
            f"""
            query FindSeed {{
                {collection}(limit: 20) {{
                    objects {{ current {{ {field} }} }}
                }}
            }}
            """
        )
        if response.errors is not None:  # the objects have no such field
            continue
        assert response.data
        return first(
            (
                uuid
                for obj in response.data[collection]["objects"]
                if obj["current"] is not None
                for uuid in collapse(obj["current"][field] or [])
            ),
            None,
        )
    return None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize("collection,filter_type,relation", RELATIONS)
def test_batched_relation_matches_unbatched(
    graphapi_post: GraphAPIPost,
    collection: str,
    filter_type: str,
    relation: str,
) -> None:
    """Batching a relation lookup must not change what it returns.

    Only a filter pinning its relation to a single UUID goes through the batched
    query, so repeating the UUID asks the same question through both code paths.

    Relations the fixture holds no objects for still cover building and running
    their batched query, which is where these queries differ from one another.
    """
    query = f"""
        query Batching($filter: {filter_type}!) {{
            {collection}(filter: $filter) {{
                objects {{ uuid }}
            }}
        }}
    """

    def read(uuids: list[str]) -> list[str]:
        response = graphapi_post(
            query, variables={"filter": {relation: {"uuids": uuids}}}
        )
        assert response.errors is None
        assert response.data
        return sorted(obj["uuid"] for obj in response.data[collection]["objects"])

    related_uuid = find_related_uuid(graphapi_post, collection, relation)
    uuid = related_uuid or str(uuid4())
    batched = read([uuid])
    unbatched = read([uuid, uuid])

    assert batched == unbatched
    # Guard against the comparison silently becoming empty on both sides.
    assert bool(batched) == bool(related_uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_batched_vacancy_filter_matches_unbatched(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
) -> None:
    """Batching must not change which managers a vacancy filter returns.

    Filtering managers by `employee: null` selects the ones nobody holds. It is
    the only filter whose batched query nests subqueries that select from the
    very relation the batch matches against.
    """
    unit = create_org_unit("unit")
    vacant = create_manager(unit)
    create_manager(unit, create_person())

    query = """
        query VacantManagers($filter: ManagerFilter!) {
            managers(filter: $filter) {
                objects { uuid }
            }
        }
    """

    def read(uuids: list[str]) -> list[UUID]:
        response = graphapi_post(
            query,
            variables={"filter": {"org_unit": {"uuids": uuids}, "employee": None}},
        )
        assert response.errors is None
        assert response.data
        return sorted(UUID(obj["uuid"]) for obj in response.data["managers"]["objects"])

    batched = read([str(unit)])
    unbatched = read([str(unit), str(unit)])

    assert batched == unbatched == [vacant]
