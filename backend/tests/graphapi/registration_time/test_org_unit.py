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
def create_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation CreateOrganisationUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.fixture
def update_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateOrganisationUnit($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_update"]["uuid"])

    return inner


@pytest.fixture
def org_unit_type(
    create_class: Callable[[dict[str, Any]], UUID], org_unit_type_facet: UUID
) -> UUID:
    return create_class(
        {
            "user_key": "department",
            "name": "Department",
            "facet_uuid": str(org_unit_type_facet),
            "validity": {"from": "1970-01-01", "to": None},
        }
    )


@pytest.fixture
def read_org_unit_registration(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]]:
        query = """
            query ReadOrganisationUnitRegistration($filter: OrganisationUnitFilter!) {
              org_units(filter: $filter) {
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
        obj = one(response.data["org_units"]["objects"])
        return obj["registrations"]

    return inner


@pytest.fixture
def read_org_unit_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], list[dict[str, Any]] | None]:
    def inner(filter: dict[str, Any]) -> list[dict[str, Any]] | None:
        query = """
            query ReadOrganisationUnitValidities($filter: OrganisationUnitFilter!) {
              org_units(filter: $filter) {
                objects {
                  validities {
                    name
                    user_key
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
        obj = only(response.data["org_units"]["objects"])
        if obj is None:
            return None
        return obj["validities"]

    return inner


@pytest.fixture
def read_org_unit_response_validities(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any], str], list[dict[str, Any]] | None]:
    def inner(
        filter: dict[str, Any], registration_time: str | None
    ) -> list[dict[str, Any]] | None:
        query = """
            query ReadOrganisationUnitResponseValidities(
              $filter: OrganisationUnitFilter!
              $registration_time: DateTime
            ) {
              org_units(filter: $filter) {
                objects {
                  validities(registration_time: $registration_time) {
                    name
                    user_key
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
        obj = only(response.data["org_units"]["objects"])
        if obj is None:
            return None
        return obj["validities"] or None

    return inner


org_unit_filter_generators = [
    # This filter is resolved using the org_unit loader
    lambda uuid, _: {"uuids": [str(uuid)]},
    # This filter is resolved using the org_unit getter
    lambda _, user_key: {"user_keys": [user_key]},
    # This filter is resolved using searching
    lambda _, user_key: {"query": user_key},
]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", org_unit_filter_generators)
def test_read_org_unit_registrations(
    create_org_unit: Callable[[dict[str, Any]], UUID],
    update_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type: UUID,
    read_org_unit_registration: Callable[[dict[str, Any]], list[dict[str, Any]]],
    read_org_unit_validities: Callable[[dict[str, Any]], list[dict[str, Any]] | None],
    read_org_unit_response_validities: Callable[
        [dict[str, Any], str | None], list[dict[str, Any]] | None
    ],
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    test_start = now()
    user_key = "root"
    org_unit_uuid = create_org_unit(
        {
            "user_key": user_key,
            "name": "Kolding Kommune",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    org_unit_filter = filter_generator(org_unit_uuid, user_key)

    # Check that we can read our newly created org_unit
    kolding = [
        {
            "user_key": user_key,
            "name": "Kolding Kommune",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_org_unit_validities(org_unit_filter)
    assert validities == kolding

    # Check that we have one and only one registration
    registration = one(read_org_unit_registration(org_unit_filter))
    assert registration == {
        "actor": str(BRUCE_UUID),
        "start": ANY,
        "end": None,
    }
    # The registration must have been created between the test-start and now
    registration_start = registration["start"]
    registration_start_time = datetime.fromisoformat(registration_start)
    assert test_start < registration_start_time < now()

    # Read the org_unit validities at varying registration times
    expected = {
        # No registration_time filter
        None: kolding,
        # Before the org_unit was registered, we expect no object result
        "1900-01-01": None,
        # Right after the org_unit was registered, we expect our org_unit
        registration_start_time.isoformat(): kolding,
        # Far in the future, we expect our org_unit
        "3000-01-01": kolding,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {
            **org_unit_filter,
            "registration_time": registration_time,
        }
        validities = read_org_unit_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_org_unit_response_validities(
            org_unit_filter, registration_time
        )

    # Update our org_unit creating another registration
    update_uuid = update_org_unit(
        {
            "name": "Vejle Kommune",
            # These are unchanged
            "uuid": str(org_unit_uuid),
            "user_key": "root",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    assert update_uuid == org_unit_uuid

    # Check that we can read our updated state
    vejle = [
        {
            "user_key": "root",
            "name": "Vejle Kommune",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    validities = read_org_unit_validities(org_unit_filter)
    assert validities == vejle

    # Check that we have exactly two registrations
    # The first should have the same starting time as before, but a new end time
    # The last should have no end time, but its start must be equal to the priors end
    registrations = read_org_unit_registration(org_unit_filter)
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

    # Read the org_unit validities at varying registration times
    expected = {
        # No registration_time filter
        None: vejle,
        # Before the org_unit was registered
        "1900-01-01": None,
        # Right after the org_unit was first registered
        registration_start_time.isoformat(): kolding,
        # Right after the org_unit was updated
        last_registration_start_time.isoformat(): vejle,
        # Far in the future
        "3000-01-01": vejle,
    }
    for registration_time, expected_validities in expected.items():
        registration_filter = {
            **org_unit_filter,
            "registration_time": registration_time,
        }
        validities = read_org_unit_validities(registration_filter)
        assert validities == expected_validities
        # Check validities can be read either via top-level filter or via response
        assert validities == read_org_unit_response_validities(
            org_unit_filter, registration_time
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_pagination_with_registration_time(
    create_org_unit: Callable[[dict[str, Any]], UUID],
    update_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type: UUID,
    graphapi_post: GraphAPIPost,
) -> None:
    # Create two org_unit, then save a timestamp for use in registration_time filtering
    org_unit1_uuid = create_org_unit(
        {
            "user_key": "first",
            "name": "Kolding Kommune",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    org_unit2_uuid = create_org_unit(
        {
            "user_key": "second",
            "name": "Kolding Kommune",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    create_time = now()

    # These updates create a new registration to 'hide' the create one
    update_org_unit(
        {
            "uuid": str(org_unit1_uuid),
            "name": "New Name",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    update_org_unit(
        {
            "uuid": str(org_unit2_uuid),
            "name": "New Name",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query Readorg_unitResponseValidities(
            $filter: OrganisationUnitFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          org_units(filter: $filter, limit: $limit, cursor: $cursor) {
            objects {
              uuid
              validities {
                name
                user_key
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
    first_response = one(response.data["org_units"]["objects"])
    cursor = response.data["org_units"]["page_info"]["next_cursor"]
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
    second_response = one(response.data["org_units"]["objects"])

    # Our GraphQL responses may be in any order
    # We assume they are in correct order and if not we swap them
    response_1 = first_response
    response_2 = second_response
    if UUID(first_response["uuid"]) == org_unit2_uuid:
        response_1, response_2 = response_2, response_1

    # Check that we see the data as of registration_time, i.e. before update
    # This proves that registration_time is respected during pagination
    expected_1 = [
        {
            "user_key": "first",
            "name": "Kolding Kommune",
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    ]
    expected_2 = [
        {
            "user_key": "second",
            "name": "Kolding Kommune",
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
    create_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type: UUID,
    graphapi_post: GraphAPIPost,
) -> None:
    # Create two org_units so we have data to iterate
    create_org_unit(
        {
            "user_key": "first",
            "name": "Kolding Kommune",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    create_org_unit(
        {
            "user_key": "second",
            "name": "Kolding Kommune",
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )

    # Iterating through the paginated set with limit=1 and a registration_time
    query = """
        query Readorg_unitResponseValidities(
            $filter: OrganisationUnitFilter!
            $limit: int!
            $cursor: Cursor
        ) {
          org_units(filter: $filter, limit: $limit, cursor: $cursor) {
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
    cursor = response.data["org_units"]["page_info"]["next_cursor"]
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
                "org_units",
            ],
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("filter_generator", org_unit_filter_generators)
def test_different_registration_times_via_aliassing(
    create_org_unit: Callable[[dict[str, Any]], UUID],
    update_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type: UUID,
    graphapi_post: GraphAPIPost,
    filter_generator: Callable[[UUID, str], dict[str, Any]],
) -> None:
    test_start_time = now()

    user_key = "0101700000"
    org_unit_uuid = create_org_unit(
        {
            "name": "Alpha",
            "user_key": user_key,
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    alpha_time = now()

    update_org_unit(
        {
            "uuid": str(org_unit_uuid),
            "name": "Beta",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    beta_time = now()

    update_org_unit(
        {
            "uuid": str(org_unit_uuid),
            "name": "Gamma",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    gamma_time = now()

    query = """
        query Readorg_unitResponseValidities(
            $filter: OrganisationUnitFilter!
            $test_start_time: DateTime!
            $alpha_time: DateTime!
            $beta_time: DateTime!
            $gamma_time: DateTime!
        ) {
          org_units(filter: $filter) {
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
    org_unit_filter = filter_generator(org_unit_uuid, user_key)
    response = graphapi_post(
        query=query,
        variables={
            "filter": org_unit_filter,
            "test_start_time": test_start_time.isoformat(),
            "alpha_time": alpha_time.isoformat(),
            "beta_time": beta_time.isoformat(),
            "gamma_time": gamma_time.isoformat(),
        },
    )
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit == {
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
    org_unit1_created = 2
    org_unit2_created = 3
    org_unit1_updated = 4
    org_unit2_updated = 5
    now = 6


@pytest.fixture
def temporally_spread_org_units_data(
    create_org_unit: Callable[[dict[str, Any]], UUID],
    update_org_unit: Callable[[dict[str, Any]], UUID],
    org_unit_type: UUID,
) -> tuple[dict[StateKey, datetime], UUID, str, UUID, str]:
    test_start_time = now()

    org_unit1_user_key = "0101700000"
    org_unit1_uuid = create_org_unit(
        {
            "name": "Created",
            "user_key": org_unit1_user_key,
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    org_unit1_created_time = now()

    org_unit2_user_key = "0101700001"
    org_unit2_uuid = create_org_unit(
        {
            "name": "Created",
            "user_key": org_unit2_user_key,
            "org_unit_type": str(org_unit_type),
            "validity": {
                "from": "1970-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    )
    org_unit2_created_time = now()

    update_org_unit(
        {
            "uuid": str(org_unit1_uuid),
            "name": "Updated",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    org_unit1_updated_time = now()

    update_org_unit(
        {
            "uuid": str(org_unit2_uuid),
            "name": "Updated",
            "validity": {
                "from": "1970-01-01",
                "to": None,
            },
        }
    )
    org_unit2_updated_time = now()

    return (
        {
            StateKey.test_start: test_start_time,
            StateKey.org_unit1_created: org_unit1_created_time,
            StateKey.org_unit2_created: org_unit2_created_time,
            StateKey.org_unit1_updated: org_unit1_updated_time,
            StateKey.org_unit2_updated: org_unit2_updated_time,
        },
        org_unit1_uuid,
        org_unit1_user_key,
        org_unit2_uuid,
        org_unit2_user_key,
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
    for org_unit1_state_key, org_unit2_state_key in state_key_permutations:
        org_unit1_expected = calculate_expected(
            org_unit1_state_key, StateKey.org_unit1_created, StateKey.org_unit1_updated
        )
        org_unit2_expected = calculate_expected(
            org_unit2_state_key, StateKey.org_unit2_created, StateKey.org_unit2_updated
        )
        yield (
            org_unit1_state_key,
            org_unit2_state_key,
            org_unit1_expected,
            org_unit2_expected,
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("org_unit1_filter_generator", org_unit_filter_generators)
@pytest.mark.parametrize("org_unit2_filter_generator", org_unit_filter_generators)
@pytest.mark.parametrize(
    "org_unit1_state_key, org_unit2_state_key, org_unit1_expected, org_unit2_expected",
    test_generator(),
)
def test_different_registration_times_on_toplevel(
    temporally_spread_org_units_data: tuple[dict[StateKey, Any], UUID, str, UUID, str],
    org_unit1_state_key: StateKey,
    org_unit2_state_key: StateKey,
    org_unit1_expected: dict[str, Any] | None,
    org_unit2_expected: dict[str, Any] | None,
    org_unit1_filter_generator: Callable[[UUID, str], dict[str, Any]],
    org_unit2_filter_generator: Callable[[UUID, str], dict[str, Any]],
    graphapi_post: GraphAPIPost,
) -> None:
    def read_org_units(
        p1_registration_time: datetime | None,
        p2_registration_time: datetime | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        query = """
            query Readorg_unitsResponseValidities(
                $p1_filter: OrganisationUnitFilter, $p2_filter: OrganisationUnitFilter!
            ) {
              p1: org_units(filter: $p1_filter) {
                objects {
                  validities {
                    name
                  }
                }
              }
              p2: org_units(filter: $p2_filter) {
                objects {
                  validities {
                    name
                  }
                }
              }
            }
        """
        org_unit1_filter = org_unit1_filter_generator(
            org_unit1_uuid, org_unit1_user_key
        )
        org_unit1_filter["registration_time"] = (
            p1_registration_time.isoformat() if p1_registration_time else None
        )
        org_unit2_filter = org_unit2_filter_generator(
            org_unit2_uuid, org_unit2_user_key
        )
        org_unit2_filter["registration_time"] = (
            p2_registration_time.isoformat() if p2_registration_time else None
        )

        response = graphapi_post(
            query=query,
            variables={
                "p1_filter": org_unit1_filter,
                "p2_filter": org_unit2_filter,
            },
        )
        assert response.errors is None
        assert response.data
        org_unit1 = only(response.data["p1"]["objects"])
        org_unit2 = only(response.data["p2"]["objects"])
        return org_unit1, org_unit2

    time_map, org_unit1_uuid, org_unit1_user_key, org_unit2_uuid, org_unit2_user_key = (
        temporally_spread_org_units_data
    )
    org_unit1_time = time_map.get(org_unit1_state_key)
    org_unit2_time = time_map.get(org_unit2_state_key)

    org_unit1, org_unit2 = read_org_units(org_unit1_time, org_unit2_time)
    assert org_unit1 == org_unit1_expected
    assert org_unit2 == org_unit2_expected
