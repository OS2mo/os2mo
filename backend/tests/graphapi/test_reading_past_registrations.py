# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from mora.util import now
from more_itertools import first
from more_itertools import last
from more_itertools import one
from more_itertools import only

from ..conftest import GraphAPIPost


@pytest.fixture
def actor_uuid() -> UUID:
    return UUID("99e7b256-7dfa-4ee8-95c6-e3abe82e236a")


@pytest.fixture
def update_person(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdatePerson($input: EmployeeUpdateInput!) {
                employee_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["employee_update"]["uuid"])

    return inner


@pytest.fixture
def read_person_registration(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]]:
        query = """
            query ReadPersonRegistation($filter: EmployeeFilter!) {
              persons(filter: $filter) {
                objects {
                  registrations {
                    actor
                    start
                    end
                  }
                }
              }
            }
        """
        response = graphapi_post(query=query, variables={"filter": filter})
        assert response.errors is None
        assert response.data
        obj = one(response.data["persons"]["objects"])
        return obj["registrations"]

    return inner


@pytest.fixture
def read_person_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]] | None]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]] | None:
        query = """
            query ReadPersonValidities($filter: EmployeeFilter!) {
              persons(filter: $filter) {
                objects {
                  validities {
                    given_name
                    surname
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(query=query, variables={"filter": filter})
        assert response.errors is None
        assert response.data
        obj = only(response.data["persons"]["objects"])
        if obj is None:
            return None
        return obj["validities"]

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter_generator",
    [
        # This filter is resolved using the person loader
        lambda uuid, _: {"uuids": [str(uuid)]},
        # This filter is resolved using the person getter
        lambda _, cpr_number: {"cpr_numbers": cpr_number},
    ],
)
def test_read_current(
    actor_uuid: UUID,
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
    read_person_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_person_validities: Callable[[dict[str, Any]], list[dict[str, Any]]],
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    test_start = now()
    cpr_number = "0101700000"
    person_uuid = create_person(
        {
            "given_name": "Egon",
            "surname": "Olsen",
            "cpr_number": cpr_number,
        }
    )
    person_filter = filter_generator(person_uuid, cpr_number)

    # Check that we can read our newly created person
    olsen = [
        {
            "given_name": "Egon",
            "surname": "Olsen",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_person_validities(person_filter)
    assert validities == olsen

    # Check that we have one and only one registration
    registration = one(read_person_registration(person_filter))
    assert registration == {
        "actor": str(actor_uuid),
        "start": ANY,
        "end": None,
    }
    # The registration must have been created between the test-start and now
    registration_start = registration["start"]
    registration_start_time = datetime.fromisoformat(registration_start)
    assert test_start < registration_start_time < now()

    # Read the person validities at varying registration times
    expected = {
        # Before the person was registered, we expect no object result
        "1900-01-01": None,
        # Right after the person was registered, we expect our person
        registration_start_time.isoformat(): olsen,
        # Far in the future, we expect our person
        "3000-01-01": olsen,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {**person_filter, "registration_time": registration_time}
        validities = read_person_validities(registration_filter)
        assert validities == expected_validities

    # Update our person creating another registration
    update_uuid = update_person(
        {
            "uuid": str(person_uuid),
            "surname": "Newsen",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    assert update_uuid == person_uuid

    # Check that we can read our updated state
    newsen = [
        {
            "given_name": "Egon",
            "surname": "Newsen",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_person_validities(person_filter)
    assert validities == newsen

    # Check that we have exactly two registrations
    # The first should have the same starting time as before, but a new end time
    # The last should have no end time, but its start must be equal to the priors end
    registrations = read_person_registration(person_filter)
    assert registrations == [
        {
            "actor": str(actor_uuid),
            "start": registration_start,
            "end": ANY,
        },
        {
            "actor": str(actor_uuid),
            "start": ANY,
            "end": None,
        },
    ]
    # Firsts end and lasts start must be equal
    first_registration_end_time = datetime.fromisoformat(first(registrations)["end"])
    last_registration_start_time = datetime.fromisoformat(last(registrations)["start"])
    assert first_registration_end_time == last_registration_start_time
    # Firsts start must be before its end
    assert registration_start_time < first_registration_end_time

    # Read the person validities at varying registration times
    expected = {
        # Before the person was registered
        "1900-01-01": None,
        # Right after the person was first registered
        registration_start_time.isoformat(): olsen,
        # Right after the person was updated
        last_registration_start_time.isoformat(): newsen,
        # Far in the future
        "3000-01-01": newsen,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {**person_filter, "registration_time": registration_time}
        validities = read_person_validities(registration_filter)
        assert validities == expected_validities


# TODO: Test reading validities on response object in the past
