# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from hypothesis import given
from mock import patch
from parameterized import parameterized
from pytest import MonkeyPatch

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
    async def test_success(self, given_name, given_cprno):
        with patch("mora.lora.Scope.create") as mock_create:
            mock_create.side_effect = lambda *args: args[-1]

            with patch(
                "mora.service.employee.validator.does_employee_with_cpr_already_exist"
            ):
                # GraphQL
                mutation_func = "employee_create"
                query = (
                    f"mutation($name: String!, $cpr_no: String!) {{"
                    f"{mutation_func}(input: {{name: $name, cpr_no: $cpr_no}}) "
                    f"{{ uuid }}"
                    f"}}"
                )

                response = await get_schema().execute(
                    query,
                    variable_values={
                        "name": given_name,
                        "cpr_no": given_cprno,
                    },
                )

                # Asserts
                mock_create.assert_called()
                assert not response.errors
                assert response.data

                uuid = None
                try:
                    # Verify the returned UUID can be parsed
                    uuid = UUID(response.data.get(mutation_func, {}).get("uuid", ""))
                except Exception:
                    uuid = uuid

                assert uuid
                assert len(str(uuid)) > 0
