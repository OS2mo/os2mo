# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_timestamp_parsing(graphapi_post: GraphAPIPost):
    """Test that GraphQL timestamp-parsing works as expected."""
    # Create employee with a very old birthday (cpr)
    create_response = graphapi_post(
        """
        mutation CreateEmployee {
          employee_create(
            input: {
              cpr_number: "0105857144",
              given_name: "Gammel",
              surname: "Gammelsen",
            }
          ) {
            uuid
          }
        }
        """
    )
    assert create_response.errors is None
    employee_uuid = create_response.data["employee_create"]["uuid"]

    # Look it up based on its CPR number
    cpr_lookup = graphapi_post(
        """
        query CPRQuery {
          employees(filter: {cpr_numbers: "0105857144"}) {
            objects {
              validities(start: null, end: null) {
                uuid
              }
            }
          }
        }
        """
    )
    assert cpr_lookup.errors is None
    assert (
        cpr_lookup.data["employees"]["objects"][0]["validities"][0]["uuid"]
        == employee_uuid
    )

    # Look it up based on its implied validity date
    validity_lookup = graphapi_post(
        """
        query ValidityQuery {
          employees(filter: {from_date: null, to_date: "1885-05-01"}) {
            objects {
              validities(start: null, end: null) {
                uuid
              }
            }
          }
        }
        """
    )
    assert validity_lookup.errors is None
    assert (
        validity_lookup.data["employees"]["objects"][0]["validities"][0]["uuid"]
        == employee_uuid
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_dates_dont_leak(graphapi_post: GraphAPIPost):
    """Test that GraphQL dates don't leak across resolvers."""
    # Create employee from 2000-01-01
    create = graphapi_post(
        """
        mutation CreateEmployee {
          employee_create(
            input: {
              given_name: "Alice",
              surname: "2000",
              cpr_number: "0101004058",
            }
          ) {
            uuid
          }
        }
        """
    )
    assert create.errors is None
    employee_uuid = create.data["employee_create"]["uuid"]

    # Query the employee twice, but with different to_date filter
    query = """
      query Employees(
        $uuid: UUID!,
        $to_date_1: DateTime = null,
        $to_date_2: DateTime = null,
      ) {
        e1: employees(filter: {uuids: [$uuid], from_date: null, to_date: $to_date_1}) {
          ...EmployeeResponsePagedFragment
        }
        e2: employees(filter: {uuids: [$uuid], from_date: null, to_date: $to_date_2}) {
          ...EmployeeResponsePagedFragment
        }
      }
      fragment EmployeeResponsePagedFragment on EmployeeResponsePaged {
        objects {
          validities {
            uuid
            validity {
              from
              to
            }
          }
        }
      }
    """

    # The result should be the same regardless of the order of the to_date filters
    query_1 = graphapi_post(
        query,
        variables={
            "uuid": employee_uuid,
            "to_date_1": "1990-01-01",
            "to_date_2": None,
        },
    )
    query_2 = graphapi_post(
        query,
        variables={
            "uuid": employee_uuid,
            "to_date_1": None,
            "to_date_2": "1990-01-01",
        },
    )
    assert query_1.errors is None
    assert query_2.errors is None
    assert query_1.data["e1"] == query_2.data["e2"]
    assert query_1.data["e2"] == query_2.data["e1"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "input_validity,expected_validity",
    [
        # Date
        (
            {"from": "2020-01-01", "to": "2020-02-01"},
            {"from": "2020-01-01T00:00:00+01:00", "to": "2020-02-01T00:00:00+01:00"},
        ),
        # Datetime
        (
            {"from": "2020-01-01T00:00:00+01:00", "to": "2020-02-01T00:00:00+01:00"},
            {"from": "2020-01-01T00:00:00+01:00", "to": "2020-02-01T00:00:00+01:00"},
        ),
    ],
)
async def test_integration_datetimes(
    graphapi_post: GraphAPIPost, input_validity: dict, expected_validity: dict
) -> None:
    """Test that GraphQL dates aren't messed with.

    Previously, MO would sometimes subtract a day from the end-date.
    """
    primary_type_facet_uuid = "1f6f34d8-d065-4bb7-9af0-738d25dc0fbf"
    create = graphapi_post(
        """
        mutation Create($facet_uuid: UUID!, $validity: ValidityInput!) {
          class_create(
            input: {
              facet_uuid: $facet_uuid
              name: "foo"
              user_key: "foo"
              validity: $validity
            }
          ) {
            uuid
          }
        }
        """,
        variables={
            "facet_uuid": primary_type_facet_uuid,
            "validity": input_validity,
        },
    )
    assert create.errors is None
    uuid = create.data["class_create"]["uuid"]

    read = graphapi_post(
        """
        query Read($uuid: UUID!) {
          classes(filter: { uuids: [$uuid], from_date: null, to_date: null }) {
            objects {
              validities(start: null, end: null) {
                validity {
                  from
                  to
                }
              }
            }
          }
        }
        """,
        variables={
            "uuid": uuid,
        },
    )
    assert read.errors is None
    read_object = one(read.data["classes"]["objects"])
    read_validity = one(read_object["validities"])
    read_validity_interval = read_validity["validity"]
    assert read_validity_interval == expected_validity
