# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
This file contains tests proving the equivalence between reading data from the
temporal axis via `Response`'s `registrations` field versus reading it from the
specific collection top-level fields (e.g. 'facets') using registration_time filter or
by passing registration_time to the `current` field on `Response`.

It is sufficient to prove equivalence with the collections using the `registration_time`
filter as that behavior is already extensively tested within the
`tests/graphapi/registration_time/*.py` tests.

This file only tests equivalence for `Facet` as the code path is identical for all
registration types, as they all utilize the same generic 'ResponseRegistration' class.

A very similar test-suite is found in backend/tests/test_model_registration.py
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from graphql import build_schema
from graphql import introspection_from_schema
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.fixture
def facet_with_two_registrations(
    create_facet: Callable[[dict[str, Any]], UUID],
    update_facet: Callable[[dict[str, Any]], UUID],
) -> None:
    # Create a Facet (Registration 1)
    facet_uuid = create_facet(
        {
            "user_key": "create",
            "validity": {"from": "2020-01-01T00:00:00+00:00"},
        }
    )

    # Update the Facet (Registration 2)
    update_facet(
        {
            "uuid": str(facet_uuid),
            "user_key": "update",
            "validity": {"from": "2022-01-01T00:00:00+00:00"},
        }
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "facet_with_two_registrations")
@pytest.mark.parametrize(
    "query_comparison",
    [
        pytest.param(
            """
            query FacetsWithQueryFilter($registration_time: DateTime!) {
                facets(filter: {registration_time: $registration_time}) {
                    objects {
                        current(registration_time: $registration_time) {
                            user_key
                        }
                    }
                }
            }
            """,
            id="query_filter",
        ),
        pytest.param(
            """
            query FacetsWithCurrentFilter($registration_time: DateTime!) {
                facets {
                    objects {
                        current(registration_time: $registration_time) {
                            user_key
                        }
                    }
                }
            }
            """,
            id="current_filter",
        ),
    ],
)
def test_facet_registration_equivalence(
    graphapi_post: GraphAPIPost,
    query_comparison: str,
) -> None:
    """Verify equivalence between the registations and current with filter."""
    # Query the registrations collection
    query_registrations = """
        query Registrations {
            facets {
                objects {
                    registrations {
                        start
                        current {
                            user_key
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query_registrations)
    assert response.errors is None
    assert response.data is not None
    objects = one(response.data["facets"]["objects"])["registrations"]
    # We expect one create and one update registration
    assert len(objects) == 2

    # Ensure that the parameterized query is equivalent
    for reg_obj in objects:
        registration_time = reg_obj["start"]
        expected_user_key = reg_obj["current"]["user_key"]

        response = graphapi_post(
            query_comparison,
            variables={
                "registration_time": registration_time,
            },
        )
        assert response.errors is None
        assert response.data is not None
        facet_obj = one(response.data["facets"]["objects"])
        actual_user_key = facet_obj["current"]["user_key"]

        assert actual_user_key == expected_user_key


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "facet_with_two_registrations")
@pytest.mark.parametrize(
    "query_comparison",
    [
        pytest.param(
            """
            query FacetsWithQueryFilterAt($registration_time: DateTime!, $at: DateTime!) {
                facets(filter: {registration_time: $registration_time}) {
                    objects {
                        current(at: $at, registration_time: $registration_time) {
                            user_key
                        }
                    }
                }
            }
            """,
            id="query_filter",
        ),
        pytest.param(
            """
            query FacetsWithCurrentFilterAt($registration_time: DateTime!, $at: DateTime!) {
                facets {
                    objects {
                        current(registration_time: $registration_time, at: $at) {
                            user_key
                        }
                    }
                }
            }
            """,
            id="current_filter",
        ),
    ],
)
@pytest.mark.parametrize(
    "at",
    [
        # Distant past
        pytest.param("1000-01-01T00:00:00+00:00", id="distant_past"),
        # Creation boundary (2020-01-01)
        pytest.param("2019-12-31T23:59:59+00:00", id="before_creation"),
        pytest.param("2020-01-01T00:00:00+00:00", id="at_creation"),
        pytest.param("2020-01-01T00:00:01+00:00", id="after_creation"),
        # Update boundary (2021-01-01)
        pytest.param("2020-12-31T23:59:59+00:00", id="before_update"),
        pytest.param("2021-01-01T00:00:00+00:00", id="at_update"),
        pytest.param("2021-01-01T00:00:01+00:00", id="after_update"),
        # Distant future
        pytest.param("3000-01-01T00:00:00+00:00", id="distant_future"),
    ],
)
def test_facet_registration_equivalence_with_at(
    graphapi_post: GraphAPIPost,
    query_comparison: str,
    at: str,
) -> None:
    """Verify equivalence while the `at` argument is being passed.

    Note: This test is similar to the one above, except this one tests equivalence when
          the `at` argument is being passed as well.
    """
    # Query the registrations collection
    query_registrations = """
        query RegistrationsWithAt($at: DateTime!) {
            facets {
                objects {
                    registrations {
                        start
                        current(at: $at) {
                            user_key
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(
        query_registrations,
        variables={"at": at},
    )
    assert response.errors is None
    assert response.data is not None
    objects = one(response.data["facets"]["objects"])["registrations"]
    # We expect one create and one update registration
    assert len(objects) == 2

    # Ensure that the parameterized query is equivalent
    for reg_obj in objects:
        registration_time = reg_obj["start"]
        # If the facet has not yet been created (i.e. at < facet creation),
        # current will be None, which must be handled here
        expected_user_key = (reg_obj.get("current") or {}).get("user_key")

        response = graphapi_post(
            query_comparison,
            variables={
                "registration_time": registration_time,
                "at": at,
            },
        )
        assert response.errors is None
        assert response.data is not None
        facet_obj = one(response.data["facets"]["objects"])
        actual_user_key = (facet_obj.get("current") or {}).get("user_key")

        assert actual_user_key == expected_user_key


@pytest.mark.parametrize("temporal_field_name", ["current", "validities"])
def test_temporal_field_argument_consistency(temporal_field_name: str) -> None:
    """Verify field equivalence for FacetResponseRegistration and FacetResponse.

    This test uses introspection on the GraphQL schema to prove that the
    FacetRegistration and FacetResponse models both take the same arguments in their
    `current` and `validities` fields.

    I.e. that the argument list at (1) and (2) are both the same:
    ```graphql
    {
        facets {
            objects {
                registrations {
                    current(
                        at: "2022-01-01"  # <--- (1)
                    ) {
                        user_key
                    }
                }
            }
        }

        facets {
            objects {
                current(
                    at: "2022-01-01",  # <--- (2)
                    registration_time: "..."
                ) {
                    user_key
                }
            }
        }
    }
    ````
    With the exception that former does not accept the `registration_time` parameter
    (since it is implicitly passed by the context) while the former accept it.

    Thus this is in essence a test to ensure that the list of fields on `current` and
    `validities` in `ResponseRegistration` match with the list of fields on `current`
    and `validities` in `Response` itself.
    """
    schema_sdl = get_schema(LATEST_VERSION).as_str()
    schema = build_schema(schema_sdl)
    introspection = introspection_from_schema(schema)

    types = introspection["__schema"]["types"]

    def find_by_name(collection: list, name: str) -> Any:
        return one(element for element in collection if element["name"] == name)

    def get_type(name: str) -> dict[str, Any]:
        return find_by_name(types, name)

    # Find the arguments taken by the temporal field on FacetRegistration
    reg_type = get_type("FacetResponseRegistration")
    reg_fields = reg_type["fields"]
    reg_temporal_field = find_by_name(reg_fields, temporal_field_name)
    reg_args_list = reg_temporal_field["args"]
    reg_args = {arg["name"]: arg for arg in reg_args_list}

    # Find the arguments taken by the temporal field on Response[Facet] (FacetResponse)
    facet_type = get_type("FacetResponse")
    facet_fields = facet_type["fields"]
    facet_temporal_field = find_by_name(facet_fields, temporal_field_name)
    facet_args_list = facet_temporal_field["args"]
    facet_args = {arg["name"]: arg for arg in facet_args_list}

    # Assert that FacetResponse.current / validities must have `registration_time`
    assert "registration_time" in facet_args
    # Assert that FacetRegistration.current / validities does not
    assert "registration_time" not in reg_args

    # Assert that both collections take the same arguments (i.e. 'at', 'start', 'end'),
    # if we remove `registration_time` from FacetResponse.
    del facet_args["registration_time"]
    assert set(facet_args.keys()) == set(reg_args.keys())
    # Assert that all arguments have the same types as well
    for arg_name in facet_args:
        assert facet_args[arg_name]["type"] == reg_args[arg_name]["type"]
