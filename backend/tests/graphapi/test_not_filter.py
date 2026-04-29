# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from ..conftest import GraphAPIPost


def _query_uuids(
    graphapi_post: GraphAPIPost,
    collection: str,
    filter_type: str,
    filter: dict,
) -> set[str]:
    """Run `<collection>(filter: ...)` and return the set of result UUIDs."""
    query = f"""
        query Q($filter: {filter_type}) {{
            {collection}(filter: $filter) {{
                objects {{ uuid }}
            }}
        }}
    """
    response = graphapi_post(query, variables={"filter": filter})
    assert response.errors is None
    assert response.data is not None
    return {obj["uuid"] for obj in response.data[collection]["objects"]}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_engagements(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit = create_org_unit("test_org_unit", None)
    person = create_person(None)
    base = {
        "engagement_type": str(uuid4()),
        "job_function": str(uuid4()),
        "org_unit": str(org_unit),
        "person": str(person),
        "validity": {"from": "1970-01-01T00:00:00Z"},
    }
    keep = create_engagement({**base, "user_key": "keep"})
    drop = create_engagement({**base, "user_key": "drop"})

    all_uuids = _query_uuids(graphapi_post, "engagements", "EngagementFilter", {})
    assert all_uuids == {str(keep), str(drop)}

    excluded = _query_uuids(
        graphapi_post,
        "engagements",
        "EngagementFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}

    # Empty user_keys list is a no-op.
    excluded = _query_uuids(
        graphapi_post,
        "engagements",
        "EngagementFilter",
        {"not": {"user_keys": []}},
    )
    assert excluded == {str(keep), str(drop)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_org_units(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
) -> None:
    keep = create_org_unit("keep")
    drop = create_org_unit("drop")

    excluded = _query_uuids(
        graphapi_post,
        "org_units",
        "OrganisationUnitFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_employees(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    keep = create_person({"given_name": "Keep", "surname": "Person", "user_key": "keep"})
    drop = create_person({"given_name": "Drop", "surname": "Person", "user_key": "drop"})

    excluded = _query_uuids(
        graphapi_post,
        "employees",
        "EmployeeFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_itsystems(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
) -> None:
    keep = create_itsystem(
        {"user_key": "keep", "name": "Keep", "validity": {"from": "2010-01-01"}}
    )
    drop = create_itsystem(
        {"user_key": "drop", "name": "Drop", "validity": {"from": "2010-01-01"}}
    )

    excluded = _query_uuids(
        graphapi_post,
        "itsystems",
        "ITSystemFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_classes(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    facet = create_facet(
        {"user_key": "test_facet", "validity": {"from": "2010-01-01"}}
    )
    keep = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "keep",
            "name": "Keep",
            "validity": {"from": "2010-01-01"},
        }
    )
    drop = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "drop",
            "name": "Drop",
            "validity": {"from": "2010-01-01"},
        }
    )

    excluded = _query_uuids(
        graphapi_post,
        "classes",
        "ClassFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_facets(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
) -> None:
    keep = create_facet({"user_key": "keep", "validity": {"from": "2010-01-01"}})
    drop = create_facet({"user_key": "drop", "validity": {"from": "2010-01-01"}})

    excluded = _query_uuids(
        graphapi_post,
        "facets",
        "FacetFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_itusers(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    person = create_person(None)
    itsystem = create_itsystem(
        {"user_key": "system", "name": "Sys", "validity": {"from": "2010-01-01"}}
    )
    keep = create_ituser(
        {
            "user_key": "keep",
            "itsystem": str(itsystem),
            "person": str(person),
            "validity": {"from": "2010-01-01"},
        }
    )
    drop = create_ituser(
        {
            "user_key": "drop",
            "itsystem": str(itsystem),
            "person": str(person),
            "validity": {"from": "2010-01-01"},
        }
    )

    excluded = _query_uuids(
        graphapi_post,
        "itusers",
        "ITUserFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_managers(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    person = create_person(None)

    def _create_manager(user_key: str) -> UUID:
        response = graphapi_post(
            """
                mutation CreateManager($input: ManagerCreateInput!) {
                    manager_create(input: $input) { uuid }
                }
            """,
            variables={
                "input": {
                    "user_key": user_key,
                    "manager_level": str(uuid4()),
                    "manager_type": str(uuid4()),
                    "responsibility": [],
                    "org_unit": str(org_unit),
                    "person": str(person),
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_create"]["uuid"])

    keep = _create_manager("keep")
    drop = _create_manager("drop")

    excluded = _query_uuids(
        graphapi_post,
        "managers",
        "ManagerFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_associations(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    person = create_person(None)
    facet = create_facet({"user_key": "assoc_facet", "validity": {"from": "2010-01-01"}})
    association_type = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "type",
            "name": "Type",
            "validity": {"from": "2010-01-01"},
        }
    )

    def _create_association(user_key: str) -> UUID:
        response = graphapi_post(
            """
                mutation CreateAssociation($input: AssociationCreateInput!) {
                    association_create(input: $input) { uuid }
                }
            """,
            variables={
                "input": {
                    "user_key": user_key,
                    "org_unit": str(org_unit),
                    "person": str(person),
                    "association_type": str(association_type),
                    "validity": {"from": "2010-01-01"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["association_create"]["uuid"])

    keep = _create_association("keep")
    drop = _create_association("drop")

    excluded = _query_uuids(
        graphapi_post,
        "associations",
        "AssociationFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_kles(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    number_facet = create_facet(
        {"user_key": "kle_number", "validity": {"from": "2010-01-01"}}
    )
    aspect_facet = create_facet(
        {"user_key": "kle_aspect", "validity": {"from": "2010-01-01"}}
    )
    kle_number = create_class(
        {
            "facet_uuid": str(number_facet),
            "user_key": "n",
            "name": "N",
            "validity": {"from": "2010-01-01"},
        }
    )
    kle_aspect = create_class(
        {
            "facet_uuid": str(aspect_facet),
            "user_key": "a",
            "name": "A",
            "validity": {"from": "2010-01-01"},
        }
    )

    def _create_kle(user_key: str) -> UUID:
        response = graphapi_post(
            """
                mutation CreateKLE($input: KLECreateInput!) {
                    kle_create(input: $input) { uuid }
                }
            """,
            variables={
                "input": {
                    "user_key": user_key,
                    "org_unit": str(org_unit),
                    "kle_number": str(kle_number),
                    "kle_aspects": [str(kle_aspect)],
                    "validity": {"from": "2010-01-01"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["kle_create"]["uuid"])

    keep = _create_kle("keep")
    drop = _create_kle("drop")

    excluded = _query_uuids(
        graphapi_post,
        "kles",
        "KLEFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_leaves(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    person = create_person(None)
    engagement = create_engagement(
        {
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(org_unit),
            "person": str(person),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    def _create_leave(user_key: str) -> UUID:
        response = graphapi_post(
            """
                mutation CreateLeave($input: LeaveCreateInput!) {
                    leave_create(input: $input) { uuid }
                }
            """,
            variables={
                "input": {
                    "user_key": user_key,
                    "person": str(person),
                    "engagement": str(engagement),
                    "leave_type": str(uuid4()),
                    "validity": {"from": "2010-01-01"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["leave_create"]["uuid"])

    keep = _create_leave("keep")
    drop = _create_leave("drop")

    excluded = _query_uuids(
        graphapi_post,
        "leaves",
        "LeaveFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_rolebindings(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
) -> None:
    person = create_person(None)
    itsystem = create_itsystem(
        {"user_key": "sys", "name": "Sys", "validity": {"from": "2010-01-01"}}
    )
    ituser = create_ituser(
        {
            "user_key": "u",
            "itsystem": str(itsystem),
            "person": str(person),
            "validity": {"from": "2010-01-01"},
        }
    )
    role_facet = create_facet(
        {"user_key": "role_facet", "validity": {"from": "2010-01-01"}}
    )
    role = create_class(
        {
            "facet_uuid": str(role_facet),
            "user_key": "role",
            "name": "Role",
            "it_system_uuid": str(itsystem),
            "validity": {"from": "2010-01-01"},
        }
    )

    keep = create_rolebinding(
        {
            "user_key": "keep",
            "ituser": str(ituser),
            "role": str(role),
            "validity": {"from": "2010-01-01"},
        }
    )
    drop = create_rolebinding(
        {
            "user_key": "drop",
            "ituser": str(ituser),
            "role": str(role),
            "validity": {"from": "2010-01-01"},
        }
    )

    excluded = _query_uuids(
        graphapi_post,
        "rolebindings",
        "RoleBindingFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_owners(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    owner_person = create_person(None)

    def _create_owner(user_key: str) -> UUID:
        response = graphapi_post(
            """
                mutation CreateOwner($input: OwnerCreateInput!) {
                    owner_create(input: $input) { uuid }
                }
            """,
            variables={
                "input": {
                    "user_key": user_key,
                    "org_unit": str(org_unit),
                    "owner": str(owner_person),
                    "validity": {"from": "2010-01-01"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["owner_create"]["uuid"])

    keep = _create_owner("keep")
    drop = _create_owner("drop")

    excluded = _query_uuids(
        graphapi_post,
        "owners",
        "OwnerFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_not_filter_related_units(graphapi_post: GraphAPIPost) -> None:
    """Fixture data has two related_units with user_keys 'rod <-> fil' (validity
    2017-2019) and 'rod <-> hum' (validity 2016-infinity). We query at a date
    where both are active."""
    in_window = {"from_date": "2018-01-01T00:00:00+01:00"}
    all_uuids = _query_uuids(
        graphapi_post, "related_units", "RelatedUnitFilter", in_window
    )
    assert len(all_uuids) == 2

    excluded = _query_uuids(
        graphapi_post,
        "related_units",
        "RelatedUnitFilter",
        {**in_window, "not": {"user_keys": ["rod <-> fil"]}},
    )
    assert len(excluded) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_not_filter_addresses(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit = create_org_unit("ou", None)
    facet = create_facet(
        {"user_key": "addr_type_facet", "validity": {"from": "2010-01-01"}}
    )
    address_type = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "EMAIL",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2010-01-01"},
        }
    )
    keep = create_address(
        {
            "user_key": "keep",
            "value": "keep@example.org",
            "address_type": str(address_type),
            "org_unit": str(org_unit),
            "validity": {"from": "2010-01-01"},
        }
    )
    drop = create_address(
        {
            "user_key": "drop",
            "value": "drop@example.org",
            "address_type": str(address_type),
            "org_unit": str(org_unit),
            "validity": {"from": "2010-01-01"},
        }
    )

    excluded = _query_uuids(
        graphapi_post,
        "addresses",
        "AddressFilter",
        {"not": {"user_keys": ["drop"]}},
    )
    assert excluded == {str(keep)}
