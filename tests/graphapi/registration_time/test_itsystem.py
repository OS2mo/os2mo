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
def read_itsystem_registration(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]]:
        query = """
            query ReadITSystemRegistration($filter: ITSystemFilter!) {
              itsystems(filter: $filter) {
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
        obj = one(response.data["itsystems"]["objects"])
        return obj["registrations"]

    return inner


@pytest.fixture
def read_itsystem_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]] | None]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]] | None:
        query = """
            query ReadITSystemValidities($filter: ITSystemFilter!) {
              itsystems(filter: $filter) {
                objects {
                  validities {
                    name
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
        obj = only(response.data["itsystems"]["objects"])
        if obj is None:
            return None
        return obj["validities"]

    return inner


@pytest.fixture
def read_itsystem_response_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any], str], list[dict[str, Any]] | None]:
    def inner(
        filter: dict[str, Any], registration_time: str | None
    ) -> list[dict[str, Any]] | None:
        query = """
            query ReadITSystemResponseValidities(
              $filter: ITSystemFilter!
              $registration_time: DateTime
            ) {
              itsystems(filter: $filter) {
                objects {
                  validities(registration_time: $registration_time) {
                    name
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
        obj = only(response.data["itsystems"]["objects"])
        if obj is None:
            return None
        return obj["validities"] or None

    return inner


# Different filters take entirely different paths through the backend
# Using these filters as parameterizations help to ensure that all codepaths are tested
itsystem_filter_generators = [
    # This filter is resolved using the ITSystem loader
    lambda uuid, _: {"uuids": [str(uuid)]},
    # This filter is resolved using the ITSystem getter
    lambda _, user_key: {"user_keys": [user_key]},
]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", itsystem_filter_generators)
def test_read_itsystem_registrations(
    create_itsystem: Callable[[dict[str, Any]], UUID],
    update_itsystem: Callable[[dict[str, Any]], UUID],
    read_itsystem_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_itsystem_validities: Callable[[dict[str, Any]], list[dict[str, Any]] | None],
    read_itsystem_response_validities: Callable[
        [dict[str, Any], str | None], list[dict[str, Any]] | None
    ],
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    """Test that we can read objects at any registration time."""
    test_start = now()
    user_key = "ad"
    itsystem_uuid = create_itsystem(
        {
            "name": "Active Directory",
            "user_key": user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem_filter = filter_generator(itsystem_uuid, user_key)

    # Check that we can read our newly created itsystem
    active_directory = [
        {
            "name": "Active Directory",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_itsystem_validities(itsystem_filter)
    assert validities == active_directory

    # Check that we have one and only one registration
    registration = one(read_itsystem_registration(itsystem_filter))
    assert registration == {
        "actor": str(BRUCE_UUID),
        "start": ANY,
        "end": None,
    }
    # The registration must have been created between the test-start and now
    registration_start = registration["start"]
    registration_start_time = datetime.fromisoformat(registration_start)
    assert test_start < registration_start_time < now()

    # Read the itsystem validities at varying registration times
    expected = {
        # No registration_time filter
        None: active_directory,
        # Before the itsystem was registered, we expect no object result
        "1900-01-01": None,
        # Right after the itsystem was registered, we expect our itsystem
        registration_start_time.isoformat(): active_directory,
        # Far in the future, we expect our itsystem
        "3000-01-01": active_directory,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {
            **itsystem_filter,
            "registration_time": registration_time,
        }
        validities = read_itsystem_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_itsystem_response_validities(
            itsystem_filter, registration_time
        )

    # Update our itsystem creating another registration
    update_uuid = update_itsystem(
        {
            "uuid": str(itsystem_uuid),
            "name": "Azure Active Directory",
            "user_key": user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    assert update_uuid == itsystem_uuid

    # Check that we can read our updated state
    azure_ad = [
        {
            "name": "Azure Active Directory",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_itsystem_validities(itsystem_filter)
    assert validities == azure_ad

    # Check that we have exactly two registrations
    # The first should have the same starting time as before, but a new end time
    # The last should have no end time, but its start must be equal to the priors end
    registrations = read_itsystem_registration(itsystem_filter)
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

    # Read the itsystem validities at varying registration times
    expected = {
        # No registration_time filter
        None: azure_ad,
        # Before the itsystem was registered
        "1900-01-01": None,
        # Right after the itsystem was first registered
        registration_start_time.isoformat(): active_directory,
        # Right after the itsystem was updated
        last_registration_start_time.isoformat(): azure_ad,
        # Far in the future
        "3000-01-01": azure_ad,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {
            **itsystem_filter,
            "registration_time": registration_time,
        }
        validities = read_itsystem_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_itsystem_response_validities(
            itsystem_filter, registration_time
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_pagination_with_registration_time(
    create_itsystem: Callable[[dict[str, Any]], UUID],
    update_itsystem: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that pagination respects registration time."""
    # Create two itsystems, then save a timestamp for use in registration_time filtering
    itsystem1_uuid = create_itsystem(
        {
            "name": "First IT System",
            "user_key": "first_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem2_uuid = create_itsystem(
        {
            "name": "Second IT System",
            "user_key": "second_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    create_time = now()

    # These updates create a new registration to 'hide' the create one
    update_itsystem(
        {
            "uuid": str(itsystem1_uuid),
            "name": "Updated First IT System",
            "user_key": "first_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    update_itsystem(
        {
            "uuid": str(itsystem2_uuid),
            "name": "Updated Second IT System",
            "user_key": "second_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadITSystemResponseValidities(
            $filter: ITSystemFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          itsystems(filter: $filter, limit: $limit, cursor: $cursor) {
            objects {
              uuid
              validities {
                name
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
    first_response = one(response.data["itsystems"]["objects"])
    cursor = response.data["itsystems"]["page_info"]["next_cursor"]
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
    second_response = one(response.data["itsystems"]["objects"])

    # Our GraphQL responses may be in any order
    # We assume they are in correct order and if not we swap them
    response_1 = first_response
    response_2 = second_response
    if UUID(first_response["uuid"]) == itsystem2_uuid:
        response_1, response_2 = response_2, response_1

    # Check that we see the data as of registration_time, i.e. before update
    # This proves that registration_time is respected during pagination
    expected_1 = [
        {
            "name": "First IT System",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    expected_2 = [
        {
            "name": "Second IT System",
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
    create_itsystem: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that an error occurs if registration_time is modified during pagination."""
    # Create two itsystems so we have data to iterate
    create_itsystem(
        {
            "name": "First IT System",
            "user_key": "first_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    create_itsystem(
        {
            "name": "Second IT System",
            "user_key": "second_it",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query ReadITSystemResponseValidities(
            $filter: ITSystemFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          itsystems(filter: $filter, limit: $limit, cursor: $cursor) {
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
    cursor = response.data["itsystems"]["page_info"]["next_cursor"]
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
                "itsystems",
            ],
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", itsystem_filter_generators)
def test_different_registration_times_via_aliassing(
    create_itsystem: Callable[[dict[str, Any]], UUID],
    update_itsystem: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    """Test that we can read multiple different pagination times with one query."""
    test_start_time = now()

    user_key = "ad"
    itsystem_uuid = create_itsystem(
        {
            "name": "Alpha",
            "user_key": user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    alpha_time = now()

    update_itsystem(
        {
            "uuid": str(itsystem_uuid),
            "name": "Beta",
            "user_key": user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    beta_time = now()

    update_itsystem(
        {
            "uuid": str(itsystem_uuid),
            "name": "Gamma",
            "user_key": user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    gamma_time = now()

    query = """
        query ReadITSystemResponseValidities(
            $filter: ITSystemFilter!
            $test_start_time: DateTime!
            $alpha_time: DateTime!
            $beta_time: DateTime!
            $gamma_time: DateTime!
        ) {
          itsystems(filter: $filter) {
            objects {
              test_start: validities(registration_time: $test_start_time) {
                name
              }
              alpha: validities(registration_time: $alpha_time) {
                name
              }
              beta: validities(registration_time: $beta_time) {
                name
              }
              gamma: validities(registration_time: $gamma_time) {
                name
              }
              past: validities(registration_time: "2000-01-01") {
                name
              }
              future: validities(registration_time: "3000-01-01") {
                name
              }
              now: validities {
                name
              }
            }
          }
        }
    """
    itsystem_filter = filter_generator(itsystem_uuid, user_key)
    response = graphapi_post(
        query=query,
        variables={
            "filter": itsystem_filter,
            "test_start_time": test_start_time.isoformat(),
            "alpha_time": alpha_time.isoformat(),
            "beta_time": beta_time.isoformat(),
            "gamma_time": gamma_time.isoformat(),
        },
    )
    assert response.errors is None
    assert response.data
    itsystem = one(response.data["itsystems"]["objects"])
    assert itsystem == {
        "test_start": [],
        "alpha": [{"name": "Alpha"}],
        "beta": [{"name": "Beta"}],
        "gamma": [{"name": "Gamma"}],
        "past": [],
        "future": [{"name": "Gamma"}],
        "now": [{"name": "Gamma"}],
    }


class StateKey(IntEnum):
    test_start = 1
    itsystem1_created = 2
    itsystem2_created = 3
    itsystem1_updated = 4
    itsystem2_updated = 5
    now = 6


@pytest.fixture
def temporally_spread_itsystems_data(
    create_itsystem: Callable[[dict[str, Any]], UUID],
    update_itsystem: Callable[[dict[str, Any]], UUID],
) -> tuple[dict[StateKey, datetime], UUID, str, UUID, str]:
    test_start_time = now()

    itsystem1_user_key = "first_it"
    itsystem1_uuid = create_itsystem(
        {
            "name": "Created",
            "user_key": itsystem1_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem1_created_time = now()

    itsystem2_user_key = "second_it"
    itsystem2_uuid = create_itsystem(
        {
            "name": "Created",
            "user_key": itsystem2_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem2_created_time = now()

    update_itsystem(
        {
            "uuid": str(itsystem1_uuid),
            "name": "Updated",
            "user_key": itsystem1_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem1_updated_time = now()

    update_itsystem(
        {
            "uuid": str(itsystem2_uuid),
            "name": "Updated",
            "user_key": itsystem2_user_key,
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    itsystem2_updated_time = now()

    return (
        {
            StateKey.test_start: test_start_time,
            StateKey.itsystem1_created: itsystem1_created_time,
            StateKey.itsystem2_created: itsystem2_created_time,
            StateKey.itsystem1_updated: itsystem1_updated_time,
            StateKey.itsystem2_updated: itsystem2_updated_time,
        },
        itsystem1_uuid,
        itsystem1_user_key,
        itsystem2_uuid,
        itsystem2_user_key,
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
            return {"validities": [{"name": "Created"}]}
        # Created, then updated --> updated validity
        return {"validities": [{"name": "Updated"}]}

    state_key_permutations = permutations(list(StateKey), 2)
    for itsystem1_state_key, itsystem2_state_key in state_key_permutations:
        itsystem1_expected = calculate_expected(
            itsystem1_state_key, StateKey.itsystem1_created, StateKey.itsystem1_updated
        )
        itsystem2_expected = calculate_expected(
            itsystem2_state_key, StateKey.itsystem2_created, StateKey.itsystem2_updated
        )
        yield (
            itsystem1_state_key,
            itsystem2_state_key,
            itsystem1_expected,
            itsystem2_expected,
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("itsystem1_filter_generator", itsystem_filter_generators)
@pytest.mark.parametrize("itsystem2_filter_generator", itsystem_filter_generators)
@pytest.mark.parametrize(
    "itsystem1_state_key, itsystem2_state_key, itsystem1_expected, itsystem2_expected",
    test_generator(),
)
def test_different_registration_times_on_toplevel(
    temporally_spread_itsystems_data: tuple[dict[StateKey, Any], UUID, str, UUID, str],
    itsystem1_state_key: StateKey,
    itsystem2_state_key: StateKey,
    itsystem1_expected: dict[str, Any] | None,
    itsystem2_expected: dict[str, Any] | None,
    itsystem1_filter_generator: Callable[[UUID, str], dict[str, Any]],
    itsystem2_filter_generator: Callable[[UUID, str], dict[str, Any]],
    graphapi_post: GraphAPIPost,
) -> None:
    def read_itsystems(
        p1_registration_time: datetime | None,
        p2_registration_time: datetime | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        query = """
            query ReadITSystemsResponseValidities(
                $p1_filter: ITSystemFilter, $p2_filter: ITSystemFilter!
            ) {
              p1: itsystems(filter: $p1_filter) {
                objects {
                  validities {
                    name
                  }
                }
              }
              p2: itsystems(filter: $p2_filter) {
                objects {
                  validities {
                    name
                  }
                }
              }
            }
        """
        itsystem1_filter = itsystem1_filter_generator(
            itsystem1_uuid, itsystem1_user_key
        )
        itsystem1_filter["registration_time"] = (
            p1_registration_time.isoformat() if p1_registration_time else None
        )
        itsystem2_filter = itsystem2_filter_generator(
            itsystem2_uuid, itsystem2_user_key
        )
        itsystem2_filter["registration_time"] = (
            p2_registration_time.isoformat() if p2_registration_time else None
        )

        response = graphapi_post(
            query=query,
            variables={
                "p1_filter": itsystem1_filter,
                "p2_filter": itsystem2_filter,
            },
        )
        assert response.errors is None
        assert response.data
        itsystem1 = only(response.data["p1"]["objects"])
        itsystem2 = only(response.data["p2"]["objects"])
        return itsystem1, itsystem2

    time_map, itsystem1_uuid, itsystem1_user_key, itsystem2_uuid, itsystem2_user_key = (
        temporally_spread_itsystems_data
    )
    itsystem1_time = time_map.get(itsystem1_state_key)
    itsystem2_time = time_map.get(itsystem2_state_key)

    itsystem1, itsystem2 = read_itsystems(itsystem1_time, itsystem2_time)
    assert itsystem1 == itsystem1_expected
    assert itsystem2 == itsystem2_expected
