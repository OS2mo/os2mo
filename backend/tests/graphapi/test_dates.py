# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

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
