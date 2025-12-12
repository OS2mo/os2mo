# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from collections.abc import Iterator
from datetime import datetime
from enum import IntEnum
from itertools import permutations
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest
from mora.util import now
from more_itertools import first
from more_itertools import last
from more_itertools import one
from more_itertools import only

from ...conftest import BRUCE_UUID
from ...conftest import GraphAPIPost


@pytest.fixture
def read_person_registration(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]]:
        query = """
            query ReadPersonRegistration($filter: EmployeeFilter!) {
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


@pytest.fixture
def read_person_response_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any], str], list[dict[str, Any]] | None]:
    def inner(
        filter: dict[str, Any], registration_time: str | None
    ) -> list[dict[str, Any]] | None:
        query = """
            query ReadPersonResponseValidities(
              $filter: EmployeeFilter!
              $registration_time: DateTime
            ) {
              persons(filter: $filter) {
                objects {
                  validities(registration_time: $registration_time) {
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
        response = graphapi_post(
            query=query,
            variables={"filter": filter, "registration_time": registration_time},
        )
        assert response.errors is None
        assert response.data
        obj = only(response.data["persons"]["objects"])
        if obj is None:
            return None
        return obj["validities"] or None

    return inner


# Different filters take entirely different paths through the backend
# Using these filters as parameterizations help to ensure that all codepaths are tested
employee_filter_generators = [
    # This filter is resolved using the person loader
    lambda uuid, _: {"uuids": [str(uuid)]},
    # This filter is resolved using the person getter
    lambda _, cpr_number: {"cpr_numbers": cpr_number},
    # This filter is resolved using searching
    lambda _, cpr_number: {"query": cpr_number},
]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", employee_filter_generators)
def test_read_person_registrations(
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
    read_person_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_person_validities: Callable[[dict[str, Any]], list[dict[str, Any]] | None],
    read_person_response_validities: Callable[
        [dict[str, Any], str | None], list[dict[str, Any]] | None
    ],
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    """Test that we can read objects at any registration time."""
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
        "actor": str(BRUCE_UUID),
        "start": ANY,
        "end": None,
    }
    # The registration must have been created between the test-start and now
    registration_start = registration["start"]
    registration_start_time = datetime.fromisoformat(registration_start)
    assert test_start < registration_start_time < now()

    # Read the person validities at varying registration times
    expected = {
        # No registration_time filter
        None: olsen,
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
        # Check validities can be read either via top-level filter or via response
        assert validities == read_person_response_validities(
            person_filter, registration_time
        )

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
            "actor": str(BRUCE_UUID),
            "start": registration_start,
            "end": ANY,
        },
        {
            "actor": str(BRUCE_UUID),
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
        # No registration_time filter
        None: newsen,
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
        # Check validities can be read either via top-level filter or via response
        assert validities == read_person_response_validities(
            person_filter, registration_time
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_pagination_with_registration_time(
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that pagination respects registration time."""
    # Create two person, then save a timestamp for use in registration_time filtering
    person1_uuid = create_person(
        {
            "given_name": "First",
            "surname": "Employee",
            "cpr_number": "0101700000",
        }
    )
    person2_uuid = create_person(
        {
            "given_name": "Second",
            "surname": "Employee",
            "cpr_number": "0101700001",
        }
    )
    create_time = now()

    # These updates create a new registration to 'hide' the create one
    update_person(
        {
            "uuid": str(person1_uuid),
            "surname": "Person",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    update_person(
        {
            "uuid": str(person2_uuid),
            "surname": "Person",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadPersonResponseValidities(
            $filter: EmployeeFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          persons(filter: $filter, limit: $limit, cursor: $cursor) {
            objects {
              uuid
              validities {
                given_name
                surname
                validity {
                  from
                  to
                }
              }
            }
            page_info {
              next_cursor
            }
          }
        }
    """
    response = graphapi_post(
        query=query,
        variables={
            "filter": {"registration_time": create_time.isoformat()},
            "limit": 1,
        },
    )
    assert response.errors is None
    assert response.data
    first_response = one(response.data["persons"]["objects"])
    cursor = response.data["persons"]["page_info"]["next_cursor"]
    assert cursor is not None

    response = graphapi_post(
        query=query,
        variables={
            "filter": {"registration_time": create_time.isoformat()},
            "limit": 1,
            "cursor": cursor,
        },
    )
    assert response.errors is None
    assert response.data
    second_response = one(response.data["persons"]["objects"])

    # Our GraphQL responses may be in any order
    # We assume they are in correct order and if not we swap them
    response_1 = first_response
    response_2 = second_response
    if UUID(first_response["uuid"]) == person2_uuid:
        response_1, response_2 = response_2, response_1

    # Check that we see the data as of registration_time, i.e. before update
    # This proves that registration_time is respected during pagination
    expected_1 = [
        {
            "given_name": "First",
            "surname": "Employee",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    expected_2 = [
        {
            "given_name": "Second",
            "surname": "Employee",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    assert response_1["validities"] == expected_1
    assert response_2["validities"] == expected_2


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_modifying_registration_time_during_pagination(
    create_person: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that an error occurs if registration_time is modified during pagination."""
    # Create two people so we have data to iterate
    create_person(
        {
            "given_name": "First",
            "surname": "Employee",
            "cpr_number": "0101700000",
        }
    )
    create_person(
        {
            "given_name": "Second",
            "surname": "Employee",
            "cpr_number": "0101700001",
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadPersonResponseValidities(
            $filter: EmployeeFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          persons(filter: $filter, limit: $limit, cursor: $cursor) {
            page_info {
              next_cursor
            }
          }
        }
    """
    response = graphapi_post(
        query=query,
        variables={
            "filter": {"registration_time": "3000-01-01"},
            "limit": 1,
        },
    )
    assert response.errors is None
    assert response.data
    cursor = response.data["persons"]["page_info"]["next_cursor"]
    assert cursor is not None

    # Check that changing the registration_time during pagination is disallowed
    # i.e. changing 3000-01-01 to 4000-01-01, this is disallowed as the cursor decides.
    # We prefer explicitly disallowing it instead of silently failing as we find
    # explicitly failing is more compliant with the principle of least astonishment.
    response = graphapi_post(
        query=query,
        variables={
            "filter": {"registration_time": "4000-01-01"},
            "limit": 1,
            "cursor": cursor,
        },
    )
    assert response.errors == [
        {
            "locations": ANY,
            "message": "Cannot change registration_time during pagination",
            "path": [
                "persons",
            ],
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", employee_filter_generators)
def test_different_registration_times_via_aliassing(
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    """Test that we can read multiple different pagination times with one query."""
    test_start_time = now()

    cpr_number = "0101700000"
    person_uuid = create_person(
        {
            "given_name": "Alpha",
            "surname": "Male",
            "cpr_number": cpr_number,
        }
    )
    alpha_time = now()

    update_person(
        {
            "uuid": str(person_uuid),
            "given_name": "Beta",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    beta_time = now()

    update_person(
        {
            "uuid": str(person_uuid),
            "given_name": "Gamma",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    gamma_time = now()

    query = """
        query ReadPersonResponseValidities(
            $filter: EmployeeFilter!
            $test_start_time: DateTime!
            $alpha_time: DateTime!
            $beta_time: DateTime!
            $gamma_time: DateTime!
        ) {
          persons(filter: $filter) {
            objects {
              test_start: validities(registration_time: $test_start_time) {
                given_name
              }
              alpha: validities(registration_time: $alpha_time) {
                given_name
              }
              beta: validities(registration_time: $beta_time) {
                given_name
              }
              gamma: validities(registration_time: $gamma_time) {
                given_name
              }
              past: validities(registration_time: "2000-01-01") {
                given_name
              }
              future: validities(registration_time: "3000-01-01") {
                given_name
              }
              now: validities {
                given_name
              }
            }
          }
        }
    """
    person_filter = filter_generator(person_uuid, cpr_number)
    response = graphapi_post(
        query=query,
        variables={
            "filter": person_filter,
            "test_start_time": test_start_time.isoformat(),
            "alpha_time": alpha_time.isoformat(),
            "beta_time": beta_time.isoformat(),
            "gamma_time": gamma_time.isoformat(),
        },
    )
    assert response.errors is None
    assert response.data
    person = one(response.data["persons"]["objects"])
    assert person == {
        "test_start": [],
        "alpha": [{"given_name": "Alpha"}],
        "beta": [{"given_name": "Beta"}],
        "gamma": [{"given_name": "Gamma"}],
        "past": [],
        "future": [{"given_name": "Gamma"}],
        "now": [{"given_name": "Gamma"}],
    }


class StateKey(IntEnum):
    test_start = 1
    person1_created = 2
    person2_created = 3
    person1_updated = 4
    person2_updated = 5
    now = 6


@pytest.fixture
def temporally_spread_persons_data(
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
) -> tuple[dict[StateKey, datetime], UUID, str, UUID, str]:
    test_start_time = now()

    person1_cpr_number = "0101700000"
    person1_uuid = create_person(
        {
            "given_name": "Created",
            "surname": "Entity",
            "cpr_number": person1_cpr_number,
        }
    )
    person1_created_time = now()

    person2_cpr_number = "0101700001"
    person2_uuid = create_person(
        {
            "given_name": "Created",
            "surname": "Entity",
            "cpr_number": person2_cpr_number,
        }
    )
    person2_created_time = now()

    update_person(
        {
            "uuid": str(person1_uuid),
            "given_name": "Updated",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    person1_updated_time = now()

    update_person(
        {
            "uuid": str(person2_uuid),
            "given_name": "Updated",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    person2_updated_time = now()

    return (
        {
            StateKey.test_start: test_start_time,
            StateKey.person1_created: person1_created_time,
            StateKey.person2_created: person2_created_time,
            StateKey.person1_updated: person1_updated_time,
            StateKey.person2_updated: person2_updated_time,
        },
        person1_uuid,
        person1_cpr_number,
        person2_uuid,
        person2_cpr_number,
    )


def test_generator() -> Iterator[
    tuple[StateKey, StateKey, dict[str, Any] | None, dict[str, Any] | None]
]:
    def calculate_expected(
        state_key: StateKey, created: StateKey, updated: StateKey
    ) -> dict[str, Any] | None:
        # No created yet --> no validities
        if state_key < created:
            return None
        # Created, but not yet updated --> created validity
        elif state_key < updated:
            return {"validities": [{"given_name": "Created"}]}
        # Created, then updated --> updated validity
        return {"validities": [{"given_name": "Updated"}]}

    state_key_permutations = permutations(list(StateKey), 2)
    for person1_state_key, person2_state_key in state_key_permutations:
        person1_expected = calculate_expected(
            person1_state_key, StateKey.person1_created, StateKey.person1_updated
        )
        person2_expected = calculate_expected(
            person2_state_key, StateKey.person2_created, StateKey.person2_updated
        )
        yield person1_state_key, person2_state_key, person1_expected, person2_expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("person1_filter_generator", employee_filter_generators)
@pytest.mark.parametrize("person2_filter_generator", employee_filter_generators)
@pytest.mark.parametrize(
    "person1_state_key, person2_state_key, person1_expected, person2_expected",
    test_generator(),
)
def test_different_registration_times_on_toplevel(
    temporally_spread_persons_data: tuple[dict[StateKey, Any], UUID, str, UUID, str],
    person1_state_key: StateKey,
    person2_state_key: StateKey,
    person1_expected: dict[str, Any] | None,
    person2_expected: dict[str, Any] | None,
    person1_filter_generator: Callable[[UUID, str], dict[str, Any]],
    person2_filter_generator: Callable[[UUID, str], dict[str, Any]],
    graphapi_post: GraphAPIPost,
) -> None:
    def read_people(
        p1_registration_time: datetime | None,
        p2_registration_time: datetime | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        query = """
            query ReadPersonsResponseValidities(
                $p1_filter: EmployeeFilter, $p2_filter: EmployeeFilter!
            ) {
              p1: persons(filter: $p1_filter) {
                objects {
                  validities {
                    given_name
                  }
                }
              }
              p2: persons(filter: $p2_filter) {
                objects {
                  validities {
                    given_name
                  }
                }
              }
            }
        """
        person1_filter = person1_filter_generator(person1_uuid, person1_cpr_number)
        person1_filter["registration_time"] = (
            p1_registration_time.isoformat() if p1_registration_time else None
        )
        person2_filter = person2_filter_generator(person2_uuid, person2_cpr_number)
        person2_filter["registration_time"] = (
            p2_registration_time.isoformat() if p2_registration_time else None
        )

        response = graphapi_post(
            query=query,
            variables={
                "p1_filter": person1_filter,
                "p2_filter": person2_filter,
            },
        )
        assert response.errors is None
        assert response.data
        person1 = only(response.data["p1"]["objects"])
        person2 = only(response.data["p2"]["objects"])
        return person1, person2

    time_map, person1_uuid, person1_cpr_number, person2_uuid, person2_cpr_number = (
        temporally_spread_persons_data
    )
    person1_time = time_map.get(person1_state_key)
    person2_time = time_map.get(person2_state_key)

    person1, person2 = read_people(person1_time, person2_time)
    assert person1 == person1_expected
    assert person2 == person2_expected
