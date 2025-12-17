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
def address_type_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {
            "user_key": "address_type_facet",
            "validity": {"from": "1970-01-01", "to": None},
        }
    )


@pytest.fixture
def address_type_uuid(
    create_class: Callable[[dict[str, Any]], UUID],
    address_type_facet: UUID,
) -> UUID:
    return create_class(
        {
            "user_key": "address_type",
            "name": "Address Type",
            "facet_uuid": str(address_type_facet),
            "scope": "TEXT",
            "validity": {"from": "1970-01-01", "to": None},
        }
    )


@pytest.fixture
def default_person_uuid(
    create_person: Callable[[dict[str, Any] | None], UUID],
) -> UUID:
    return create_person(None)


@pytest.fixture
def read_address_registration(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]]:
        query = """
            query ReadAddressRegistration($filter: AddressFilter!) {
              addresses(filter: $filter) {
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
        obj = one(response.data["addresses"]["objects"])
        return obj["registrations"]

    return inner


@pytest.fixture
def read_address_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]] | None]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]] | None:
        query = """
            query ReadAddressValidities($filter: AddressFilter!) {
              addresses(filter: $filter) {
                objects {
                  validities {
                    value
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
        obj = only(response.data["addresses"]["objects"])
        if obj is None:
            return None
        return obj["validities"]

    return inner


@pytest.fixture
def read_address_response_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any], str], list[dict[str, Any]] | None]:
    def inner(
        filter: dict[str, Any], registration_time: str | None
    ) -> list[dict[str, Any]] | None:
        query = """
            query ReadAddressResponseValidities(
              $filter: AddressFilter!
              $registration_time: DateTime
            ) {
              addresses(filter: $filter) {
                objects {
                  validities(registration_time: $registration_time) {
                    value
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
        obj = only(response.data["addresses"]["objects"])
        if obj is None:
            return None
        return obj["validities"] or None

    return inner


# Different filters take entirely different paths through the backend
# Using these filters as parameterizations help to ensure that all codepaths are tested
address_filter_generators = [
    # This filter is resolved using the address loader
    lambda uuid, _: {"uuids": [str(uuid)]},
    # This filter is resolved using the address getter
    lambda _, user_key: {"user_keys": [user_key]},
]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", address_filter_generators)
def test_read_address_registrations(
    create_address: Callable[[dict[str, Any]], UUID],
    update_address: Callable[[dict[str, Any]], UUID],
    read_address_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_address_validities: Callable[[dict[str, Any]], list[dict[str, Any]] | None],
    read_address_response_validities: Callable[
        [dict[str, Any], str | None], list[dict[str, Any]] | None
    ],
    filter_generator: Callable[[UUID, str], dict[str, Any]],
    address_type_uuid: UUID,
    default_person_uuid: UUID,
) -> None:
    """Test that we can read objects at any registration time."""
    test_start = now()
    address_user_key = "AddressUserKey"
    address_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Home",
            "user_key": address_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address_filter = filter_generator(address_uuid, address_user_key)

    # Check that we can read our newly created address
    home = [
        {
            "value": "Home",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_address_validities(address_filter)
    assert validities == home

    # Check that we have one and only one registration
    registration = one(read_address_registration(address_filter))
    assert registration == {
        "actor": str(BRUCE_UUID),
        "start": ANY,
        "end": None,
    }
    # The registration must have been created between the test-start and now
    registration_start = registration["start"]
    registration_start_time = datetime.fromisoformat(registration_start)
    assert test_start < registration_start_time < now()

    # Read the address validities at varying registration times
    expected = {
        # No registration_time filter
        None: home,
        # Before the address was registered, we expect no object result
        "1900-01-01": None,
        # Right after the address was registered, we expect our address
        registration_start_time.isoformat(): home,
        # Far in the future, we expect our address
        "3000-01-01": home,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {**address_filter, "registration_time": registration_time}
        validities = read_address_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_address_response_validities(
            address_filter, registration_time
        )

    # Update our address creating another registration
    update_uuid = update_address(
        {
            "uuid": str(address_uuid),
            "address_type": str(address_type_uuid),
            "value": "Sweet Home",
            "user_key": address_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    assert update_uuid == address_uuid

    # Check that we can read our updated state
    sweet_home = [
        {
            "value": "Sweet Home",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_address_validities(address_filter)
    assert validities == sweet_home

    # Check that we have exactly two registrations
    # The first should have the same starting time as before, but a new end time
    # The last should have no end time, but its start must be equal to the priors end
    registrations = read_address_registration(address_filter)
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

    # Read the address validities at varying registration times
    expected = {
        # No registration_time filter
        None: sweet_home,
        # Before the address was registered
        "1900-01-01": None,
        # Right after the address was first registered
        registration_start_time.isoformat(): home,
        # Right after the address was updated
        last_registration_start_time.isoformat(): sweet_home,
        # Far in the future
        "3000-01-01": sweet_home,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {**address_filter, "registration_time": registration_time}
        validities = read_address_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_address_response_validities(
            address_filter, registration_time
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_pagination_with_registration_time(
    create_address: Callable[[dict[str, Any]], UUID],
    update_address: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
    address_type_uuid: UUID,
    default_person_uuid: UUID,
) -> None:
    """Test that pagination respects registration time."""
    # Create two addresses, then save a timestamp for use in registration_time filtering
    address1_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "First Address",
            "user_key": "First Address Key",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address2_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Second Address",
            "user_key": "Second Address Key",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    create_time = now()

    # These updates create a new registration to 'hide' the create one
    update_address(
        {
            "uuid": str(address1_uuid),
            "address_type": str(address_type_uuid),
            "value": "Updated First Address",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    update_address(
        {
            "uuid": str(address2_uuid),
            "address_type": str(address_type_uuid),
            "value": "Updated Second Address",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadAddressResponseValidities(
            $filter: AddressFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          addresses(filter: $filter, limit: $limit, cursor: $cursor) {
            objects {
              uuid
              validities {
                value
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
    first_response = one(response.data["addresses"]["objects"])
    cursor = response.data["addresses"]["page_info"]["next_cursor"]
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
    second_response = one(response.data["addresses"]["objects"])

    # Our GraphQL responses may be in any order
    # We assume they are in correct order and if not we swap them
    response_1 = first_response
    response_2 = second_response
    if UUID(first_response["uuid"]) == address2_uuid:
        response_1, response_2 = response_2, response_1

    # Check that we see the data as of registration_time, i.e. before update
    # This proves that registration_time is respected during pagination
    expected_1 = [
        {
            "value": "First Address",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    expected_2 = [
        {
            "value": "Second Address",
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
    create_address: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
    address_type_uuid: UUID,
    default_person_uuid: UUID,
) -> None:
    """Test that an error occurs if registration_time is modified during pagination."""
    # Create two addresses so we have data to iterate
    create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "First Address",
            "user_key": "First Address Key",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Second Address",
            "user_key": "Second Address Key",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadAddressResponseValidities(
            $filter: AddressFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          addresses(filter: $filter, limit: $limit, cursor: $cursor) {
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
    cursor = response.data["addresses"]["page_info"]["next_cursor"]
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
                "addresses",
            ],
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", address_filter_generators)
def test_different_registration_times_via_aliassing(
    create_address: Callable[[dict[str, Any]], UUID],
    update_address: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
    filter_generator: Callable[[UUID, str], dict[str, Any]],
    address_type_uuid: UUID,
    default_person_uuid: UUID,
) -> None:
    """Test that we can read multiple different pagination times with one query."""
    test_start_time = now()

    address_user_key = "AddressUserKey"
    address_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Alpha",
            "user_key": address_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    alpha_time = now()

    update_address(
        {
            "uuid": str(address_uuid),
            "address_type": str(address_type_uuid),
            "value": "Beta",
            "user_key": address_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    beta_time = now()

    update_address(
        {
            "uuid": str(address_uuid),
            "address_type": str(address_type_uuid),
            "value": "Gamma",
            "user_key": address_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    gamma_time = now()

    query = """
        query ReadAddressResponseValidities(
            $filter: AddressFilter!
            $test_start_time: DateTime!
            $alpha_time: DateTime!
            $beta_time: DateTime!
            $gamma_time: DateTime!
        ) {
          addresses(filter: $filter) {
            objects {
              test_start: validities(registration_time: $test_start_time) {
                value
              }
              alpha: validities(registration_time: $alpha_time) {
                value
              }
              beta: validities(registration_time: $beta_time) {
                value
              }
              gamma: validities(registration_time: $gamma_time) {
                value
              }
              past: validities(registration_time: "2000-01-01") {
                value
              }
              future: validities(registration_time: "3000-01-01") {
                value
              }
              now: validities {
                value
              }
            }
          }
        }
    """
    address_filter = filter_generator(address_uuid, address_user_key)
    response = graphapi_post(
        query=query,
        variables={
            "filter": address_filter,
            "test_start_time": test_start_time.isoformat(),
            "alpha_time": alpha_time.isoformat(),
            "beta_time": beta_time.isoformat(),
            "gamma_time": gamma_time.isoformat(),
        },
    )
    assert response.errors is None
    assert response.data
    address = one(response.data["addresses"]["objects"])
    assert address == {
        "test_start": [],
        "alpha": [{"value": "Alpha"}],
        "beta": [{"value": "Beta"}],
        "gamma": [{"value": "Gamma"}],
        "past": [],
        "future": [{"value": "Gamma"}],
        "now": [{"value": "Gamma"}],
    }


class StateKey(IntEnum):
    test_start = 1
    address1_created = 2
    address2_created = 3
    address1_updated = 4
    address2_updated = 5
    now = 6


@pytest.fixture
def temporally_spread_addresses_data(
    create_address: Callable[[dict[str, Any]], UUID],
    update_address: Callable[[dict[str, Any]], UUID],
    address_type_uuid: UUID,
    default_person_uuid: UUID,
) -> tuple[dict[StateKey, datetime], UUID, str, UUID, str]:
    test_start_time = now()

    address1_user_key = "first_addr"
    address1_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Created",
            "user_key": address1_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address1_created_time = now()

    address2_user_key = "second_addr"
    address2_uuid = create_address(
        {
            "address_type": str(address_type_uuid),
            "person": str(default_person_uuid),
            "value": "Created",
            "user_key": address2_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address2_created_time = now()

    update_address(
        {
            "uuid": str(address1_uuid),
            "address_type": str(address_type_uuid),
            "value": "Updated",
            "user_key": address1_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address1_updated_time = now()

    update_address(
        {
            "uuid": str(address2_uuid),
            "address_type": str(address_type_uuid),
            "value": "Updated",
            "user_key": address2_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    address2_updated_time = now()
    return (
        {
            StateKey.test_start: test_start_time,
            StateKey.address1_created: address1_created_time,
            StateKey.address2_created: address2_created_time,
            StateKey.address1_updated: address1_updated_time,
            StateKey.address2_updated: address2_updated_time,
        },
        address1_uuid,
        address1_user_key,
        address2_uuid,
        address2_user_key,
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
            return {"validities": [{"value": "Created"}]}
        # Created, then updated --> updated validity
        return {"validities": [{"value": "Updated"}]}

    state_key_permutations = permutations(list(StateKey), 2)
    for address1_state_key, address2_state_key in state_key_permutations:
        address1_expected = calculate_expected(
            address1_state_key, StateKey.address1_created, StateKey.address1_updated
        )
        address2_expected = calculate_expected(
            address2_state_key, StateKey.address2_created, StateKey.address2_updated
        )
        yield (
            address1_state_key,
            address2_state_key,
            address1_expected,
            address2_expected,
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("address1_filter_generator", address_filter_generators)
@pytest.mark.parametrize("address2_filter_generator", address_filter_generators)
@pytest.mark.parametrize(
    "address1_state_key, address2_state_key, address1_expected, address2_expected",
    test_generator(),
)
def test_different_registration_times_on_toplevel(
    temporally_spread_addresses_data: tuple[dict[StateKey, Any], UUID, str, UUID, str],
    address1_state_key: StateKey,
    address2_state_key: StateKey,
    address1_expected: dict[str, Any] | None,
    address2_expected: dict[str, Any] | None,
    address1_filter_generator: Callable[[UUID, str], dict[str, Any]],
    address2_filter_generator: Callable[[UUID, str], dict[str, Any]],
    graphapi_post: GraphAPIPost,
) -> None:
    def read_addresses(
        p1_registration_time: datetime | None,
        p2_registration_time: datetime | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        query = """
            query ReadAddressesResponseValidities(
                $p1_filter: AddressFilter, $p2_filter: AddressFilter!
            ) {
              p1: addresses(filter: $p1_filter) {
                objects {
                  validities {
                    value
                  }
                }
              }
              p2: addresses(filter: $p2_filter) {
                objects {
                  validities {
                    value
                  }
                }
              }
            }
        """
        address1_filter = address1_filter_generator(address1_uuid, address1_user_key)
        address1_filter["registration_time"] = (
            p1_registration_time.isoformat() if p1_registration_time else None
        )
        address2_filter = address2_filter_generator(address2_uuid, address2_user_key)
        address2_filter["registration_time"] = (
            p2_registration_time.isoformat() if p2_registration_time else None
        )

        response = graphapi_post(
            query=query,
            variables={
                "p1_filter": address1_filter,
                "p2_filter": address2_filter,
            },
        )
        assert response.errors is None
        assert response.data
        address1 = only(response.data["p1"]["objects"])
        address2 = only(response.data["p2"]["objects"])
        return address1, address2

    time_map, address1_uuid, address1_user_key, address2_uuid, address2_user_key = (
        temporally_spread_addresses_data
    )
    address1_time = time_map.get(address1_state_key)
    address2_time = time_map.get(address2_state_key)

    address1, address2 = read_addresses(address1_time, address2_time)
    assert address1 == address1_expected
    assert address2 == address2_expected
