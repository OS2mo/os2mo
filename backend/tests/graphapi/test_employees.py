# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime
from itertools import product
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from parameterized import parameterized
from pytest import MonkeyPatch

import tests.cases
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import mapping
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import EmployeeCreate
from mora.graphapi.versions.latest.types import EmployeeType
from mora.util import NEGATIVE_INFINITY
from ramodels.mo import EmployeeRead
from tests.conftest import GQLResponse

# Helpers
now_beginning = datetime.datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=0
)


@given(test_data=graph_data_strat(EmployeeRead))
def test_query_all(test_data, graphapi_post, patch_loader):
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
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
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


class TestEmployeeTerminate(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(
        [
            (
                "3b866d97-0b1f-48e0-8078-686d96f430b3",
                NEGATIVE_INFINITY,
                now_beginning,
                True,
            ),
            (
                "3b866d97-0b1f-48e0-8078-686d96f430b3",
                now_beginning,
                now_beginning,
                True,
            ),
            ("3b866d97-0b1f-48e0-8078-686d96f430b3", None, now_beginning, True),
            ("3b866d97-0b1f-48e0-8078-686d96f430b3", now_beginning, None, False),
            ("3b866d97-0b1f-48e0-8078-686d96f430b3", None, None, False),
            (None, now_beginning, None, False),
            (None, None, now_beginning, False),
            (None, None, None, False),
        ]
    )
    @pytest.mark.slow
    async def test_mutator(
        self, given_uuid, given_from_date, given_to_date, expected_result
    ):
        with patch("mora.lora.Scope.get_all") as mock_lora_get_all, patch(
            "mora.service.handlers.get_handler_for_function"
        ) as mock_get_handler_for_function, patch(
            "mora.common.add_history_entry"
        ) as mock_add_history_entry:
            # Mocking
            mock_lora_get_all.return_value = {
                given_uuid: {
                    "tilstande": {
                        "organisationenhedgyldighed": [
                            {"virkning": {mapping.FROM: NEGATIVE_INFINITY}}
                        ]
                    }
                }
            }.items()

            mock_request_handler_submit = AsyncMock()
            mock_request_handler_construct = AsyncMock(
                return_value=AsyncMock(submit=mock_request_handler_submit)
            )

            mock_get_handler_for_function.return_value = AsyncMock(
                construct=mock_request_handler_construct,
            )

            # Invoke GraphQL
            mutation_func = "employee_terminate"
            query, var_values = self._get_graphql_query_and_vars(
                mutation_func,
                uuid=given_uuid,
                from_date=given_from_date,
                to_date=given_to_date,
            )

            response = await execute_graphql(query, variable_values=var_values)

            # Asserts
            if expected_result:
                mock_lora_get_all.assert_called()
                mock_get_handler_for_function.assert_called()
                mock_add_history_entry.assert_called()

                mock_request_handler_construct.assert_called()
                mock_request_handler_submit.assert_called()

                assert (
                    response.data.get(mutation_func, {}).get("uuid", None) == given_uuid
                )
            else:
                mock_lora_get_all.assert_not_called()
                mock_get_handler_for_function.assert_not_called()
                mock_add_history_entry.assert_not_called()

                mock_request_handler_construct.assert_not_called()
                mock_request_handler_submit.assert_not_called()

    @parameterized.expand(
        [
            (
                "3b866d97-0b1f-48e0-8078-686d96f430b3",
                NEGATIVE_INFINITY,
                now_beginning,
                True,
            ),
            (
                "3b866d97-0b1f-48e0-8078-686d96f430b3",
                now_beginning,
                now_beginning,
                True,
            ),
            ("3b866d97-0b1f-48e0-8078-686d96f430b3", "", now_beginning, True),
            ("3b866d97-0b1f-48e0-8078-686d96f430b3", "", "", False),
            ("", now_beginning, "", False),
            ("", "", now_beginning, False),
            ("", NEGATIVE_INFINITY, now_beginning, False),
            ("", "", "", False),
        ]
    )
    async def test_pydantic_dataclass(
        self, given_uuid, given_from_date, given_to_date, expected_result
    ):
        with patch(
            "mora.graphapi.versions.latest.mutators.terminate_employee"
        ) as mock_terminate_employee:
            # Invoke GraphQL
            mutation_func = "employee_terminate"
            query, var_values = self._get_graphql_query_and_vars(
                mutation_func,
                uuid=given_uuid,
                from_date=given_from_date,
                to_date=given_to_date,
            )

            _ = await execute_graphql(query, variable_values=var_values)

            if expected_result:
                mock_terminate_employee.assert_called()
            else:
                mock_terminate_employee.assert_not_called()

    @staticmethod
    def _get_graphql_query_and_vars(
        mutation_func: str = "employee_terminate", **kwargs
    ):
        query = (
            f"mutation($uuid: UUID!, $from: DateTime, $to: DateTime!, "
            f"$triggerless: Boolean) {{"
            f"{mutation_func}(input: {{uuid: $uuid, from: $from, to: $to, "
            f"triggerless: $triggerless}}) "
            f"{{ uuid }}"
            f"}}"
        )

        var_values = {}
        uuid = kwargs.get("uuid")
        if uuid:
            var_values["uuid"] = uuid

        from_date = kwargs.get("from_date")
        if from_date:
            var_values["from"] = from_date.isoformat()

        to_date = kwargs.get("to_date")
        if to_date:
            var_values["to"] = to_date.isoformat()

        return query, var_values


# Create lists of possible values
test_mutator_success_uuids = [
    "00000000-0000-0000-0000-000000000000",
    "720d3063-9649-4371-9c38-5a8af04b96dd",
]
test_mutator_fail_uuids = [None]
test_mutator_names = [None, "Jens Jensen"]
test_mutator_nickname_firsts = [None, "Jens"]
test_mutator_nickname_lasts = [None, "Lyn"]

test_pydantic_dataclass_uuids_success = test_mutator_success_uuids
test_pydantic_dataclass_uuids_fail = ["", "something-darkside"]
test_pydantic_dataclass_names = ["", "Jens Jensen"]
test_pydantic_dataclass_nickname_firsts = ["", "Jens"]
test_pydantic_dataclass_nickname_lasts = ["", "Lyn"]

# Create parm lists
test_mutator_success_params = list(
    product(
        test_mutator_success_uuids,
        test_mutator_names,
        test_mutator_nickname_firsts,
        test_mutator_nickname_lasts,
    )
)
test_mutator_fail_params = list(
    product(
        test_mutator_fail_uuids,
        test_mutator_names,
        test_mutator_nickname_firsts,
        test_mutator_nickname_lasts,
    )
)

test_pydantic_dataclass_success_params = list(
    product(
        test_pydantic_dataclass_uuids_success,
        test_pydantic_dataclass_names,
        test_pydantic_dataclass_nickname_firsts,
        test_pydantic_dataclass_nickname_lasts,
    )
)
test_pydantic_dataclass_fail_params = list(
    product(
        test_pydantic_dataclass_uuids_fail,
        test_pydantic_dataclass_names,
        test_pydantic_dataclass_nickname_firsts,
        test_pydantic_dataclass_nickname_lasts,
    )
)

params_test_mutator = [param + (True,) for param in test_mutator_success_params]
params_test_mutator += [param + (False,) for param in test_mutator_fail_params]

params_test_pydantic_dataclass = [
    param + (True,) for param in test_pydantic_dataclass_success_params
]
params_test_pydantic_dataclass += [
    param + (False,) for param in test_pydantic_dataclass_fail_params
]


class TestEmployeeUpdate(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(params_test_mutator)
    async def test_mutator(
        self,
        given_uuid,
        given_name,
        given_nickname_first,
        given_nickname_last,
        expected_result,
    ):
        with patch(
            "mora.graphapi.versions.latest.employee.handle_requests"
        ) as mock_handle_requests:
            mock_handle_requests.return_value = given_uuid

            # GraphQL
            mutation_func = "employee_update"
            query = (
                "mutation($uuid: UUID!, $name: String = null, $nicknameFirst: String, "
                "$nicknameLast: String) {"
                f"{mutation_func}(input: {{uuid: $uuid, name: $name, "
                "nickname_givenname: $nicknameFirst, nickname_surname: $nicknameLast}) "
                "{ uuid }"
                "}"
            )

            var_values = {}
            if given_uuid:
                var_values["uuid"] = given_uuid

            if given_name:
                var_values["name"] = given_name

            if given_nickname_first:
                var_values["nicknameFirst"] = given_nickname_first

            if given_nickname_last:
                var_values["nicknameLast"] = given_nickname_last

            response = await execute_graphql(query, variable_values=var_values)

            # Asserts
            if expected_result:
                mock_handle_requests.assert_called()

                assert (
                    response.data.get(mutation_func, {}).get("uuid", None) == given_uuid
                )
            else:
                mock_handle_requests.assert_not_called()

    @parameterized.expand(params_test_pydantic_dataclass)
    async def test_pydantic_dataclass(
        self,
        given_uuid,
        given_name,
        given_nickname_first,
        given_nickname_last,
        expected_result,
    ):
        with patch(
            "mora.graphapi.versions.latest.mutators.employee_update"
        ) as mock_employee_update:
            query = (
                "mutation($uuid: UUID!, $name: String = null, $nicknameFirst: String, "
                "$nicknameLast: String) {"
                "employee_update(input: {uuid: $uuid, name: $name, "
                "nickname_givenname: $nicknameFirst, nickname_surname: $nicknameLast}) "
                "{ uuid }"
                "}"
            )

            var_values = {}
            if given_uuid:
                var_values["uuid"] = given_uuid

            if given_name:
                var_values["name"] = given_name

            if given_nickname_first:
                var_values["nicknameFirst"] = given_nickname_first

            if given_nickname_last:
                var_values["nicknameLast"] = given_nickname_last

            _ = await execute_graphql(query, variable_values=var_values)

            if expected_result:
                mock_employee_update.assert_called()
            else:
                mock_employee_update.assert_not_called()


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.employee_create", new_callable=AsyncMock)
async def test_create_employee(
    create_employee: AsyncMock, test_data: EmployeeCreate
) -> None:
    """Test that pydantic jsons are passed through to employee_create."""

    mutate_query = """
        mutation CreateOrgUnit($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    created_uuid = uuid4()
    create_employee.return_value = EmployeeType(uuid=created_uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"employee_create": {"uuid": str(created_uuid)}}

    create_employee.assert_called_with(test_data)


@st.composite
def valid_cprs(draw) -> str:
    # TODO: Add minimum and maximum birthyears as parameters
    valid_date = draw(
        st.dates(
            min_value=datetime.date(1970, 1, 1),  # Should really start at 1857
            max_value=datetime.date(2057, 1, 1),
        )
    )
    if valid_date.year < 1900:
        # TODO: Add mixed region 5000->9000
        code = draw(st.integers(min_value=5000, max_value=9000))
    elif valid_date.year < 2000:
        # TODO: Add mixed regions 4000->5000, 5000->9000 and 9000+
        code = draw(st.integers(min_value=0, max_value=4000))
    else:
        # TODO: Add mixed regions 4000->5000 and 9000+
        code = draw(st.integers(min_value=9000, max_value=9999))
    valid_code = str(code).zfill(4)
    cpr_number = valid_date.strftime("%d%m%y") + valid_code
    return cpr_number


@patch(
    "mora.service.employee.does_employee_with_cpr_already_exist", new_callable=AsyncMock
)
@given(
    test_data=st.builds(
        EmployeeCreate,
        givenname=st.text(
            alphabet=st.characters(whitelist_categories=("L",)), min_size=1
        ),
        surname=st.text(
            alphabet=st.characters(whitelist_categories=("L",)), min_size=1
        ),
        cpr_number=st.none() | valid_cprs(),
    )
)
@pytest.mark.slow
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_employee_integration_test(
    does_employee_with_cpr_already_exist: AsyncMock,
    test_data: EmployeeCreate,
    graphapi_post,
) -> None:
    """Test that employees can be created in LoRa via GraphQL."""

    does_employee_with_cpr_already_exist.return_value = None

    mutate_query = """
        mutation CreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["employee_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            employees(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    user_key
                    givenname
                    surname
                    cpr_no
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["employees"])["objects"])
    assert obj["givenname"] == test_data.givenname
    assert obj["surname"] == test_data.surname
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert obj["cpr_no"] == test_data.cpr_number
