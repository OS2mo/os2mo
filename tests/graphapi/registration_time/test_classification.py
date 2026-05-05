# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from collections.abc import Iterator
from datetime import datetime
from enum import IntEnum
from itertools import permutations
from typing import Any
from uuid import UUID

import pytest
from mora.util import now
from more_itertools import only

from ...conftest import GraphAPIPost


class StateKey(IntEnum):
    test_start = 1
    facet_created = 2
    class_created = 3
    facet_updated = 4
    class_updated = 5
    now = 6


@pytest.fixture
def temporally_spread_classification_data(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    update_facet: Callable[[dict[str, Any]], UUID],
    update_class: Callable[[dict[str, Any]], UUID],
) -> dict[StateKey, datetime]:
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
        StateKey.test_start: test_start_time,
        StateKey.facet_created: facet_created_time,
        StateKey.class_created: class_created_time,
        StateKey.facet_updated: facet_updated_time,
        StateKey.class_updated: class_updated_time,
    }


def test_facet_generator() -> Iterator[tuple[StateKey, StateKey, dict[str, Any]]]:
    def calculate_expected(
        facet_state_key: StateKey, class_state_key: StateKey
    ) -> dict[str, Any]:
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

        facet_user_key = (
            "facet_create"
            if facet_state_key < StateKey.facet_updated
            else "facet_update"
        )
        class_user_key = (
            "class_create"
            if class_state_key < StateKey.class_updated
            else "class_update"
        )

        # If facet does not exist yet, empty result
        if facet_state_key < StateKey.facet_created:
            return {"validities": []}

        # If class does not exist yet, normal result, but without classes
        if class_state_key < StateKey.class_created:
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

    state_key_permutations = permutations(list(StateKey), 2)
    for facet_state_key, class_state_key in state_key_permutations:
        facet_expected = calculate_expected(facet_state_key, class_state_key)
        yield facet_state_key, class_state_key, facet_expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "facet_state_key, class_state_key, facet_expected", test_facet_generator()
)
def test_nested_registration_times_toplevel_facet(
    temporally_spread_classification_data: dict[str, datetime],
    facet_state_key: str,
    class_state_key: str,
    facet_expected: dict[str, Any],
    graphapi_post: GraphAPIPost,
) -> None:
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

    time_map = temporally_spread_classification_data
    facet_time = time_map.get(facet_state_key)
    class_time = time_map.get(class_state_key)

    facet = read_class_and_facet(facet_time, class_time)
    assert facet == facet_expected


def test_class_generator() -> Iterator[tuple[StateKey, StateKey, dict[str, Any]]]:
    def calculate_expected(
        facet_state_key: StateKey, class_state_key: StateKey
    ) -> dict[str, Any]:
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

        facet_user_key = (
            "facet_create"
            if facet_state_key < StateKey.facet_updated
            else "facet_update"
        )
        class_user_key = (
            "class_create"
            if class_state_key < StateKey.class_updated
            else "class_update"
        )

        # If class does not exist yet, empty result
        if class_state_key < StateKey.class_created:
            return {"validities": []}

        # If class does not exist yet, normal result, but without classes
        if facet_state_key < StateKey.facet_created:
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

    state_key_permutations = permutations(list(StateKey), 2)
    for facet_state_key, class_state_key in state_key_permutations:
        class_expected = calculate_expected(facet_state_key, class_state_key)
        yield facet_state_key, class_state_key, class_expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "facet_state_key, class_state_key, class_expected", test_class_generator()
)
def test_nested_registration_times_toplevel_class(
    temporally_spread_classification_data: dict[str, datetime],
    facet_state_key: str,
    class_state_key: str,
    class_expected: dict[str, Any],
    graphapi_post: GraphAPIPost,
) -> None:
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

    time_map = temporally_spread_classification_data
    facet_time = time_map.get(facet_state_key)
    class_time = time_map.get(class_state_key)

    clazz = read_class_and_facet(facet_time, class_time)
    assert clazz == class_expected
