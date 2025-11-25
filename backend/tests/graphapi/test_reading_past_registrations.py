# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
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
    actor_uuid: UUID,
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
    read_person_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_person_validities: Callable[[dict[str, Any]], list[dict[str, Any]] | None],
    read_person_response_validities: Callable[
        [dict[str, Any], str | None], list[dict[str, Any]] | None
    ],
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


@pytest.fixture
def temporally_spread_persons_data(
    create_person: Callable[[dict[str, Any]], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
) -> tuple[dict[str, datetime], UUID, str, UUID, str]:
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
            "test_start": test_start_time,
            "person1_created": person1_created_time,
            "person2_created": person2_created_time,
            "person1_updated": person1_updated_time,
            "person2_updated": person2_updated_time,
        },
        person1_uuid,
        person1_cpr_number,
        person2_uuid,
        person2_cpr_number,
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("person1_filter_generator", employee_filter_generators)
@pytest.mark.parametrize("person2_filter_generator", employee_filter_generators)
@pytest.mark.parametrize(
    "person1_state_key, person2_state_key",
    list(
        permutations(
            [
                "test_start",
                "person1_created",
                "person2_created",
                "person1_updated",
                "person2_updated",
                None,
            ],
            2,
        )
    ),
)
def test_different_registration_times_on_toplevel(
    temporally_spread_persons_data: tuple[dict[str, Any], UUID, str, UUID, str],
    person1_state_key: str,
    person2_state_key: str,
    person1_filter_generator: Callable[[UUID, str], dict[str, Any]],
    person2_filter_generator: Callable[[UUID, str], dict[str, Any]],
    graphapi_post: GraphAPIPost,
) -> None:
    time_map, person1_uuid, person1_cpr_number, person2_uuid, person2_cpr_number = (
        temporally_spread_persons_data
    )
    person1_time = time_map.get(person1_state_key)
    person2_time = time_map.get(person2_state_key)

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

    # How we expect person1 to look at different registration times
    person1_expected = {"validities": [{"given_name": "Updated"}]}
    if person1_time is not None:
        if person1_time < time_map["person1_created"]:
            person1_expected = None
        elif person1_time < time_map["person1_updated"]:
            person1_expected = {"validities": [{"given_name": "Created"}]}

    # How we expect person2 to look at different registration times
    person2_expected = {"validities": [{"given_name": "Updated"}]}
    if person2_time is not None:
        if person2_time < time_map["person2_created"]:
            person2_expected = None
        elif person2_time < time_map["person2_updated"]:
            person2_expected = {"validities": [{"given_name": "Created"}]}

    person1, person2 = read_people(person1_time, person2_time)
    assert person1 == person1_expected
    assert person2 == person2_expected


@pytest.fixture
def update_facet(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateFacet($input: FacetUpdateInput!) {
                facet_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["facet_update"]["uuid"])

    return inner


@pytest.fixture
def update_class(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateClass($input: ClassUpdateInput!) {
                class_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["class_update"]["uuid"])

    return inner


@pytest.fixture
def temporally_spread_classification_data(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    update_facet: Callable[[dict[str, Any]], UUID],
    update_class: Callable[[dict[str, Any]], UUID],
) -> dict[str, datetime]:
    test_start_time = now()

    facet_uuid = create_facet(
        {
            "user_key": "facet_create",
            "validity": {"from": "1970-01-01"},
        }
    )
    facet_created_time = now()

    class_uuid = create_class(
        {
            "user_key": "class_create",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(facet_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )
    class_created_time = now()

    update_facet(
        {
            "uuid": str(facet_uuid),
            "user_key": "facet_update",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    facet_updated_time = now()

    update_class(
        {
            "uuid": str(class_uuid),
            "user_key": "class_update",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(facet_uuid),
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    class_updated_time = now()

    return {
        "test_start": test_start_time,
        "facet_created": facet_created_time,
        "class_created": class_created_time,
        "facet_updated": facet_updated_time,
        "class_updated": class_updated_time,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "facet_state_key, class_state_key",
    list(
        permutations(
            [
                "test_start",
                "facet_created",
                "class_created",
                "facet_updated",
                "class_updated",
                None,
            ],
            2,
        )
    ),
)
def test_nested_registration_times_toplevel_facet(
    temporally_spread_classification_data: dict[str, datetime],
    facet_state_key: str,
    class_state_key: str,
    graphapi_post: GraphAPIPost,
) -> None:
    time_map = temporally_spread_classification_data
    facet_time = time_map.get(facet_state_key)
    class_time = time_map.get(class_state_key)

    def read_class_and_facet(
        facet_registration_time: datetime | None,
        class_registration_time: datetime | None,
    ) -> dict[str, Any] | None:
        query = """
            query ReadFacetAndClassesAtRegistrationTimes(
                $facet_registration_time: DateTime
                $class_registration_time: DateTime
            ) {
              facets {
                objects {
                  validities(registration_time: $facet_registration_time) {
                    user_key
                    classes_responses {
                      objects {
                        validities(registration_time: $class_registration_time) {
                          user_key
                        }
                      }
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(
            query=query,
            variables={
                "facet_registration_time": facet_registration_time.isoformat()
                if facet_registration_time
                else None,
                "class_registration_time": class_registration_time.isoformat()
                if class_registration_time
                else None,
            },
        )
        assert response.errors is None
        assert response.data
        facet = only(response.data["facets"]["objects"])
        return facet

    def facet_expected(facet_time: datetime | None, class_time: datetime | None):
        def gen_result(facet_user_key: str, class_user_key: str) -> dict[str, Any]:
            return {
                "validities": [
                    {
                        "user_key": facet_user_key,
                        "classes_responses": {
                            "objects": [
                                {
                                    "validities": [
                                        {
                                            "user_key": class_user_key,
                                        },
                                    ],
                                }
                            ]
                        },
                    },
                ]
            }

        # If None is given use timestamp for last registration time
        # Doing so makes it possible to compare the timestamps without handling None
        facet_time = facet_time or time_map["class_updated"]
        class_time = class_time or time_map["class_updated"]

        class_user_key = (
            "class_create" if class_time < time_map["class_updated"] else "class_update"
        )
        facet_user_key = (
            "facet_create" if facet_time < time_map["facet_updated"] else "facet_update"
        )

        # If facet does not exist yet, empty result
        if facet_time < time_map["facet_created"]:
            return {"validities": []}

        # If class does not exist yet, normal result, but without classes
        if class_time < time_map["class_created"]:
            return {
                "validities": [
                    {
                        "user_key": facet_user_key,
                        "classes_responses": {"objects": [{"validities": []}]},
                    },
                ]
            }

        # If both facet and class have been created, normal result
        return gen_result(facet_user_key, class_user_key)

    facet = read_class_and_facet(facet_time, class_time)
    assert facet == facet_expected(facet_time, class_time)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "facet_state_key, class_state_key",
    list(
        permutations(
            [
                "test_start",
                "facet_created",
                "class_created",
                "facet_updated",
                "class_updated",
                None,
            ],
            2,
        )
    ),
)
def test_nested_registration_times_toplevel_class(
    temporally_spread_classification_data: dict[str, datetime],
    facet_state_key: str,
    class_state_key: str,
    graphapi_post: GraphAPIPost,
) -> None:
    time_map = temporally_spread_classification_data
    facet_time = time_map.get(facet_state_key)
    class_time = time_map.get(class_state_key)

    def read_class_and_facet(
        facet_registration_time: datetime | None,
        class_registration_time: datetime | None,
    ) -> dict[str, Any] | None:
        query = """
            query ReadClassAndFacetAtRegistrationTimes(
                $facet_registration_time: DateTime
                $class_registration_time: DateTime
            ) {
              classes {
                objects {
                  validities(registration_time: $class_registration_time) {
                    user_key
                    facet_response {
                      validities(registration_time: $facet_registration_time) {
                        user_key
                      }
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(
            query=query,
            variables={
                "facet_registration_time": facet_registration_time.isoformat()
                if facet_registration_time
                else None,
                "class_registration_time": class_registration_time.isoformat()
                if class_registration_time
                else None,
            },
        )
        assert response.errors is None
        assert response.data
        clazz = only(response.data["classes"]["objects"])
        return clazz

    def class_expected(facet_time: datetime | None, class_time: datetime | None):
        def gen_result(facet_user_key: str, class_user_key: str) -> dict[str, Any]:
            return {
                "validities": [
                    {
                        "user_key": class_user_key,
                        "facet_response": {
                            "validities": [
                                {
                                    "user_key": facet_user_key,
                                },
                            ],
                        },
                    },
                ]
            }

        # If None is given use timestamp for last registration time
        # Doing so makes it possible to compare the timestamps without handling None
        facet_time = facet_time or time_map["class_updated"]
        class_time = class_time or time_map["class_updated"]

        class_user_key = (
            "class_create" if class_time < time_map["class_updated"] else "class_update"
        )
        facet_user_key = (
            "facet_create" if facet_time < time_map["facet_updated"] else "facet_update"
        )

        # If class does not exist yet, empty result
        if class_time < time_map["class_created"]:
            return {"validities": []}

        # If facet does not exist yet, normal result, but without facet
        if facet_time < time_map["facet_created"]:
            return {
                "validities": [
                    {
                        "user_key": class_user_key,
                        "facet_response": {"validities": []},
                    },
                ]
            }

        # If both facet and class have been created, normal result
        return gen_result(facet_user_key, class_user_key)

    clazz = read_class_and_facet(facet_time, class_time)
    assert clazz == class_expected(facet_time, class_time)


# TODO: Test cursor + registration time for org-units
# TODO: Test org-units
# TODO: Test literally alle objekt typer (alle org-funks sammen)
