# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from tests.conftest import BRUCE_UUID
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_employee(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    uuid = create_person(None)
    response = graphapi_post(
        """
        query Read($filter: EmployeeFilter) {
            employees(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_org_unit(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    uuid = create_org_unit("unit", None)
    response = graphapi_post(
        """
        query Read($filter: OrganisationUnitFilter) {
            org_units(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["org_units"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_facet(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    uuid = create_facet({"user_key": "facet_one", "validity": {"from": "2000-01-01"}})
    response = graphapi_post(
        """
        query Read($filter: FacetFilter) {
            facets(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["facets"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_class(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    facet_uuid = create_facet({"user_key": "f", "validity": {"from": "2000-01-01"}})
    uuid = create_class(
        {
            "facet_uuid": str(facet_uuid),
            "user_key": "c",
            "name": "C",
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: ClassFilter) {
            classes(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["classes"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_itsystem(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    uuid = create_itsystem(
        {
            "user_key": "s",
            "name": "S",
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: ITSystemFilter) {
            itsystems(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["itsystems"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_ituser(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    person_uuid = create_person(None)
    itsystem_uuid = create_itsystem(
        {"user_key": "s", "name": "S", "validity": {"from": "2000-01-01"}}
    )
    uuid = create_ituser(
        {
            "user_key": "u",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: ITUserFilter) {
            itusers(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["itusers"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_address(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    # address_create reads the address_type class's `scope`, so we need a real one.
    facet_uuid = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "2000-01-01"}}
    )
    address_type_uuid = create_class(
        {
            "facet_uuid": str(facet_uuid),
            "user_key": "email",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2000-01-01"},
        }
    )
    person_uuid = create_person(None)
    uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(person_uuid),
            "value": "home@example.org",
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: AddressFilter) {
            addresses(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["addresses"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_engagement(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    person_uuid = create_person(None)
    org_unit_uuid = create_org_unit("unit", None)
    uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: EngagementFilter) {
            engagements(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["engagements"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_association(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_association: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    person_uuid = create_person(None)
    org_unit_uuid = create_org_unit("unit", None)
    uuid = create_association(
        {
            "org_unit": str(org_unit_uuid),
            "employee": str(person_uuid),
            "association_type": str(uuid4()),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: AssociationFilter) {
            associations(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["associations"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_manager(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_manager: Callable[[UUID, UUID | None], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    person_uuid = create_person(None)
    org_unit_uuid = create_org_unit("unit", None)
    uuid = create_manager(org_unit_uuid, person_uuid)
    response = graphapi_post(
        """
        query Read($filter: ManagerFilter) {
            managers(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["managers"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_kle(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_kle: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    org_unit_uuid = create_org_unit("unit", None)
    uuid = create_kle(
        {
            "user_key": "k",
            "org_unit": str(org_unit_uuid),
            "kle_number": str(uuid4()),
            "kle_aspects": [str(uuid4())],
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: KLEFilter) {
            kles(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["kles"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_leave(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    person_uuid = create_person(None)
    org_unit_uuid = create_org_unit("unit", None)
    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2000-01-01"},
        }
    )
    uuid = create_leave(
        {
            "person": str(person_uuid),
            "engagement": str(engagement_uuid),
            "leave_type": str(uuid4()),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: LeaveFilter) {
            leaves(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["leaves"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "registration, expected_match",
    [
        ({"start": "2000-01-01T00:00:00Z", "end": "2100-01-01T00:00:00Z"}, True),
        ({"start": "1800-01-01T00:00:00Z", "end": "1900-01-01T00:00:00Z"}, False),
        ({"actors": [str(BRUCE_UUID)]}, True),
        ({"actors": [str(uuid4())]}, False),
    ],
)
def test_registration_filter_rolebinding(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    registration: dict[str, Any],
    expected_match: bool,
) -> None:
    itsystem_uuid = create_itsystem(
        {"user_key": "s", "name": "S", "validity": {"from": "2000-01-01"}}
    )
    role_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2000-01-01"},
        }
    )
    person_uuid = create_person(None)
    ituser_uuid = create_ituser(
        {
            "user_key": "u",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2000-01-01"},
        }
    )
    uuid = create_rolebinding(
        {
            "user_key": "rb",
            "ituser": str(ituser_uuid),
            "role": str(role_class_uuid),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        """
        query Read($filter: RoleBindingFilter) {
            rolebindings(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        {"filter": {"registration": registration}},
    )
    assert response.errors is None
    assert response.data
    uuids = {obj["uuid"] for obj in response.data["rolebindings"]["objects"]}
    assert uuids == ({str(uuid)} if expected_match else set())
