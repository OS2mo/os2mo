# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import uuid
from unittest.mock import ANY
from unittest.mock import patch

import pytest
from fastapi.encoders import jsonable_encoder
from mora.lora import ValidityLiteral
from mora.service.detail_reading import list_addresses_ou
from strawberry.types import ExecutionResult


@pytest.fixture
def get_list_addresses_ou_test_data() -> tuple[
    uuid.UUID, ValidityLiteral, datetime.date
]:
    org_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    validity_literal: ValidityLiteral = "present"
    at_attr = datetime.date(2023, 1, 5)
    return org_id, validity_literal, at_attr


@patch("mora.service.detail_reading.execute_graphql")
@patch("mora.service.detail_reading.validity_tuple")
async def test_list_addresses_ou_validity_tuple_at_attr_and_validity_literal(
    mock_validity_tuple, mock_execute_graphql, get_list_addresses_ou_test_data
):
    org_id, validity_literal, at_attr = get_list_addresses_ou_test_data
    mock_validity_tuple.return_value = (at_attr, at_attr)
    mock_execute_graphql.return_value = ExecutionResult(
        errors=None, data={"org_units": {"objects": []}}
    )

    result = await list_addresses_ou(
        orgid=org_id, at=at_attr, validity=validity_literal
    )

    mock_validity_tuple.assert_called_with(validity_literal, now=at_attr)
    assert result == []


@patch("mora.service.detail_reading.execute_graphql")
async def test_list_addresses_ou_execute_graphql_specific_date(
    mock_execute_graphql, get_list_addresses_ou_test_data
):
    org_id, validity_literal, at_attr = get_list_addresses_ou_test_data
    mock_execute_graphql.return_value = ExecutionResult(
        errors=None, data={"org_units": {"objects": []}}
    )

    result = await list_addresses_ou(
        orgid=org_id, at=at_attr, validity=validity_literal
    )

    mock_execute_graphql.assert_called_with(
        ANY,
        variable_values=jsonable_encoder(
            {
                "uuid": org_id,
                "from_date": datetime.datetime(2023, 1, 5, 0, 0, 0, 0),
                "to_date": datetime.datetime(2023, 1, 5, 0, 0, 0, 1),
            }
        ),
    )
    assert result == []
