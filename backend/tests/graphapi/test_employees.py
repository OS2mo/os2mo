# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any

from hypothesis import given
from more_itertools import one
from parameterized import parameterized
from pytest import MonkeyPatch
from strawberry.types import ExecutionResult

import mora.graphapi.dataloaders as dataloaders
import tests.cases
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.main import get_schema
from mora.graphapi.shim import flatten_data
from ramodels.mo import EmployeeRead
from tests.conftest import GQLResponse

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestEmployeesQuery:
    """Class collecting employees query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(EmployeeRead))
    def test_query_all(self, test_data, graphapi_post, patch_loader):
        """Test that we can query all our employees."""
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    employees {
                        uuid
                        objects {
                            givenname
                            surname
                            nickname_givenname
                            nickname_surname
                            cpr_no
                            seniority
                            user_key
                            type
                            uuid
                            validity {from to}
                        }
                    }
                }
            """
            response: GQLResponse = graphapi_post(query)

        assert response.errors is None
        assert response.data
        assert flatten_data(response.data["employees"]) == test_data

    @given(test_input=graph_data_uuids_strat(EmployeeRead))
    def test_query_by_uuid(self, test_input, graphapi_post, patch_loader):
        """Test that we can query employees by UUID."""
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        employees(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

        assert response.errors is None
        assert response.data

        # Check UUID equivalence
        result_uuids = [empl.get("uuid") for empl in response.data["employees"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))


class TestEmployeeCreate(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(
        [
            ("Laura Christensen", "0103882148"),
            ("Jens Jensen", "0103882149"),
        ]
    )
    async def test_create_employee(self, given_name, given_cprno):
        mutation_func = "employee_create"
        query = (
            f"mutation($name: String!, $cpr_no: String!) {{"
            f"{mutation_func}(input: {{name: $name, cpr_no: $cpr_no}}) "
            f"{{ uuid }}"
            f"}}"
        )

        response = await _execute_graphql(
            query,
            variable_values={
                "name": given_name,
                "cpr_no": given_cprno,
            },
        )
        handle_gql_error(response)

        assert 1 == True


async def _execute_graphql(*args: Any, **kwargs: Any) -> ExecutionResult:
    return await get_schema().execute(*args, **kwargs)


# Originalle from "backend/mora/service/util.py", but moved to this file since its
# located insinde the mora.service-package
def handle_gql_error(response: ExecutionResult) -> None:
    if response.errors:
        error = one(response.errors)
        if error.original_error:
            raise error.original_error
        raise ValueError(error)
