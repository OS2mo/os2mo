# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import first

from tests.conftest import GQLResponse


@patch("mora.lora.Scope.delete", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "method",
    [
        "address_delete",
        "engagement_delete",
    ],
)
async def test_delete_organisationfunktion(
    delete_mock: AsyncMock, graphapi_post, method
) -> None:
    uuid = uuid4()
    delete_mock.return_value = uuid
    mutate_query = f"""
        mutation DeleteOrganisationfunktion($uuid: UUID!) {{
          {method}(uuid: $uuid) {{
            uuid
          }}
        }}
    """
    response: GQLResponse = graphapi_post(
        mutate_query,
        variables=jsonable_encoder({"uuid": uuid}),
    )
    assert response.errors is None
    assert response.data[method]["uuid"] == str(uuid)
    delete_mock.assert_awaited_once_with(uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "organisationfunktion,method",
    [
        ("addresses", "address_delete"),
        ("engagements", "engagement_delete"),
    ],
)
async def test_delete_organisationfunktion_integration_test(
    graphapi_post, organisationfunktion, method
) -> None:
    # Read current organisationfunktion
    read_query = f"""
        query MyQuery {{
          {organisationfunktion} {{
            uuid
          }}
        }}
    """
    response: GQLResponse = graphapi_post(read_query)
    first_organisationfunktion = first(response.data[organisationfunktion])
    assert first_organisationfunktion in response.data[organisationfunktion]

    # Delete the first one
    mutate_query = f"""
        mutation DeleteOrganisationfunktion($uuid: UUID!) {{
          {method}(uuid: $uuid) {{
            uuid
          }}
        }}
    """
    response: GQLResponse = graphapi_post(
        mutate_query,
        variables={"uuid": first_organisationfunktion["uuid"]},
    )
    assert response.errors is None
    assert response.data[method]["uuid"] == first_organisationfunktion["uuid"]

    # Check that it got deleted
    response: GQLResponse = graphapi_post(read_query)
    assert organisationfunktion not in response.data[organisationfunktion]
