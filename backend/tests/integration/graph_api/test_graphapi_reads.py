# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import note
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis_graphql import strategies as gql_st
from mora.graphapi.schema import get_schema
from mora.graphapi.shim import flatten_data
from mora.graphapi.version import LATEST_VERSION
from more_itertools import all_equal
from tests.conftest import GraphAPIPost


@pytest.fixture(autouse=True)
async def load_fixture_data(fixture_db):
    """Class scoped sample structure.

    We only do reads in this integration test, so there is no reason for us to
    load data before and db_reset after every function.
    """
    yield


UUID_SEARCHABLE_FIELDS = [
    "addresses",
    "associations",
    "classes",
    "employees",
    "engagements",
    "facets",
    "itsystems",
    "itusers",
    "kles",
    "leaves",
    "managers",
    "org_units",
    "related_units",
    "rolebindings",
]
FIELDS = UUID_SEARCHABLE_FIELDS + [
    "healths",
    "org",
    "version",
    # TODO: uncomment these and make sure tests run:
    # "configuration",
    # "files",
]


@pytest.mark.integration_test
@settings(
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.function_scoped_fixture,
        # I had a much better assume statement, but the reading handlers are shit
        # so they break on all kinda of assumed non-asserted invariants.
        HealthCheck.filter_too_much,
    ],
    max_examples=10,  # These tests are slow and using hypothesis
    # for them is a bit much. Number of examples is fixed until we solve it.
)
@pytest.mark.parametrize("field", FIELDS)
@given(data=st.data())
def test_queries(data, field, graphapi_post: GraphAPIPost):
    """Test queries generated from the entire schema.

    This tests all manners of valid queries generated from the GraphAPI schema.
    We expect the status code to always be 200, and that data is available in the
    response, while errors are None.
    """
    query = data.draw(
        gql_st.query(str(get_schema(LATEST_VERSION)), fields=[field]).filter(
            lambda query: (
                "from_date: null" not in query
                # For details, see: backend/tests/graphapi/test_registration.py
                and "registrations" not in query
                and "query" not in query
                and "registration" not in query
                and "start: null" not in query
                # The inherit flag requires an organizational unit filter
                and "inherit: true" not in query
            )
        )
    )

    note(f"Failing query:\n{query}")
    response = graphapi_post(query=query)
    assert response.status_code == 200
    assert response.errors is None
    assert response.data


@pytest.mark.integration_test
class TestManagerInheritance:
    # Anders And is manager at humfak
    humfak = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    # There is no manager at filins
    filins = "85715fc7-925d-401b-822d-467eb4b163b6"

    query = """
        query TestQuery($uuids: [UUID!], $inherit: Boolean!)
        {
            org_units(filter: {uuids: $uuids}) {
                objects {
                    objects {
                        managers(inherit: $inherit) {
                            employee_uuid
                        }
                    }
                }
            }
        }
    """

    def test_manager_no_inheritance(self, graphapi_post: GraphAPIPost):
        """No inheritance - no manager for filins."""
        variables = {"uuids": [self.filins], "inherit": False}
        response = graphapi_post(query=self.query, variables=variables)
        assert response.errors is None
        assert response.data
        managers = flatten_data(response.data["org_units"]["objects"])
        assert managers == [{"managers": []}]

    def test_manager_with_inheritance(self, graphapi_post: GraphAPIPost):
        """Inheritance - Anders And is manager of both humfak & filins."""
        variables = {"uuids": [self.humfak, self.filins], "inherit": True}
        response = graphapi_post(query=self.query, variables=variables)
        assert response.errors is None
        assert response.data
        managers = flatten_data(response.data["org_units"]["objects"])
        assert all_equal(managers)


@pytest.mark.integration_test
def test_regression_51523_1(graphapi_post):
    query = """
        query TestQuery {
            org_units(filter: {uuids: ["deadbeef-dead-beef-0000-000000000000"]}) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert response.data["org_units"]["objects"] == []


@pytest.mark.integration_test
def test_regression_51523_2(graphapi_post):
    query = """
        query TestQuery {
            org_units(filter: {uuids: ["deadbeef-dead-beef-0000-000000000000"]}) {
                objects {
                    objects {
                        uuid
                    }
                }
            }
        }
    """
    response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert response.data["org_units"]["objects"] == []


@pytest.mark.integration_test
@pytest.mark.parametrize("field", UUID_SEARCHABLE_FIELDS)
def test_regression_51523_generalised(graphapi_post: GraphAPIPost, field):
    query = f"""
        query TestQuery {{
            {field}(filter: {{uuids: ["deadbeef-dead-beef-0000-000000000000"]}}) {{
                objects {{
                    uuid
                }}
            }}
        }}
    """
    response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert response.data[field]["objects"] == []
