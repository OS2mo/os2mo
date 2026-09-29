# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from tests.conftest import GraphAPIPost

PAST = {"from": "2000-01-01T00:00:00+01:00", "to": "2001-01-01T00:00:00+01:00"}
FUTURE = {"from": "2100-01-01T00:00:00+01:00", "to": None}

PURGE_MUTATION = """
    mutation PurgeEmployee($uuid: UUID!) {
        employee_purge(uuid: $uuid) {
            uuid
            addresses_response { uuid }
            associations_response { uuid }
            engagements_response { uuid }
            itusers_response { uuid }
            leaves_response { uuid }
            manager_roles_response { uuid }
            owners_response { uuid }
            ownerships_response { uuid }
        }
    }
"""

NOTHING_ACTIVE = {
    "addresses_response": [],
    "associations_response": [],
    "engagements_response": [],
    "itusers_response": [],
    "leaves_response": [],
    "manager_roles_response": [],
    "owners_response": [],
    "ownerships_response": [],
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_purge_allowed_when_nothing_is_tied_to_the_employee(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> None:
    """Test that a bare employee may be purged."""
    # Arrange
    person = create_person()

    # Act
    response = graphapi_post(PURGE_MUTATION, {"uuid": str(person)})

    # Assert
    assert response.errors is None
    assert response.data
    assert response.data["employee_purge"] == {
        "uuid": str(person),
        **NOTHING_ACTIVE,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_purge_allowed_when_everything_is_history(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
) -> None:
    """Test that objects which stopped being active do not block the purge."""
    # Arrange
    person = create_person()
    org_unit = create_org_unit("unit")
    create_engagement(
        {
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": PAST,
        }
    )

    # Act
    response = graphapi_post(PURGE_MUTATION, {"uuid": str(person)})

    # Assert
    assert response.errors is None
    assert response.data
    assert response.data["employee_purge"] == {
        "uuid": str(person),
        **NOTHING_ACTIVE,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("validity", [{"from": "2000-01-01", "to": None}, FUTURE])
def test_employee_purge_refused_while_an_engagement_is_active(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    validity: dict[str, Any],
) -> None:
    """Test that an engagement active now or in the future blocks the purge."""
    # Arrange
    person = create_person()
    org_unit = create_org_unit("unit")
    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": validity,
        }
    )

    # Act
    response = graphapi_post(PURGE_MUTATION, {"uuid": str(person)})

    # Assert
    assert response.errors is None
    assert response.data
    assert response.data["employee_purge"] == {
        "uuid": str(person),
        **NOTHING_ACTIVE,
        "engagements_response": [{"uuid": str(engagement)}],
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_purge_reports_every_kind_of_active_object(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
    create_association: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[..., UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """Test that everything tied to the employee is reported as in the way."""
    # Arrange
    person = create_person()
    other = create_person()
    org_unit = create_org_unit("unit")
    validity = {"from": "2000-01-01T00:00:00+01:00", "to": None}

    address_type_facet = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "1970-01-01"}}
    )
    address_type = create_class(
        {
            "user_key": "EmailEmployee",
            "name": "Email",
            "scope": "TEXT",
            "facet_uuid": str(address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )
    itsystem = create_itsystem(
        {
            "user_key": "ad",
            "name": "Active Directory",
            "validity": {"from": "1970-01-01"},
        }
    )

    address = create_address(
        {
            "person": str(person),
            "address_type": str(address_type),
            "value": "spam@eggs.invalid",
            "validity": validity,
        }
    )
    association = create_association(
        {
            "person": str(person),
            "org_unit": str(org_unit),
            "association_type": str(uuid4()),
            "validity": validity,
        }
    )
    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": validity,
        }
    )
    ituser = create_ituser(
        {
            "user_key": "ad-account",
            "person": str(person),
            "itsystem": str(itsystem),
            "validity": validity,
        }
    )
    leave = create_leave(
        {
            "person": str(person),
            "engagement": str(engagement),
            "leave_type": str(uuid4()),
            "validity": validity,
        }
    )
    manager_role = create_manager(org_unit, person, validity=validity)
    # The employee as the owned party, and as the owner of somebody else
    owner = create_owner(
        {"owner": str(other), "person": str(person), "validity": validity}
    )
    ownership = create_owner(
        {"owner": str(person), "person": str(other), "validity": validity}
    )

    # Act
    response = graphapi_post(PURGE_MUTATION, {"uuid": str(person)})

    # Assert
    assert response.errors is None
    assert response.data
    assert response.data["employee_purge"] == {
        "uuid": str(person),
        "addresses_response": [{"uuid": str(address)}],
        "associations_response": [{"uuid": str(association)}],
        "engagements_response": [{"uuid": str(engagement)}],
        "itusers_response": [{"uuid": str(ituser)}],
        "leaves_response": [{"uuid": str(leave)}],
        "manager_roles_response": [{"uuid": str(manager_role)}],
        "owners_response": [{"uuid": str(owner)}],
        "ownerships_response": [{"uuid": str(ownership)}],
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_purge_purges_nothing_yet(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
) -> None:
    """Test that purging leaves the employee and their objects untouched."""
    # Arrange
    person = create_person()
    org_unit = create_org_unit("unit")
    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2000-01-01T00:00:00+01:00"},
        }
    )

    read_query = """
        query ReadAll {
            employees { objects { uuid } }
            engagements { objects { uuid } }
        }
    """

    # Act
    response = graphapi_post(PURGE_MUTATION, {"uuid": str(person)})
    assert response.errors is None

    # Assert
    after = graphapi_post(read_query)
    assert after.errors is None
    assert after.data == {
        "employees": {"objects": [{"uuid": str(person)}]},
        "engagements": {"objects": [{"uuid": str(engagement)}]},
    }
