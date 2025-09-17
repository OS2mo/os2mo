# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_timestamp_parsing(graphapi_post: GraphAPIPost) -> None:
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
def test_dates_dont_leak(graphapi_post: GraphAPIPost) -> None:
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
