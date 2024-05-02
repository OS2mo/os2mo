# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "model,filter_uuid",
    [
        ("address", "414044e0-fe5f-4f82-be20-1e107ad50e80"),
        ("association", "c2153d5d-4a2b-492d-a18c-c498f7bb6221"),
        ("class", "06f95678-166a-455a-a2ab-121a8d92ea23"),
        ("engagement", "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"),
        ("facet", "1a6045a2-7a8e-4916-ab27-b2402e64f2be"),
        ("itsystem", "59c135c9-2b15-41cc-97c8-b5dff7180beb"),
        ("ituser", "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66"),
        ("kle", "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5"),
        ("leave", "0895b7f5-86ac-45c5-8fb1-c3047d45b643"),
        ("manager", "05609702-977f-4869-9fb4-50ad74c6999a"),
        ("org_unit", "5942ce50-2be8-476f-914b-6769a888a7c8"),
        ("owner", "c16ff527-3501-42f7-a942-e606c6c1a0a7"),
        # TODO (#57656): enable once employee is renamed to person
        # ("person", "236e0a78-11a0-4ed9-8545-6286bb8611c7"),
        ("related_unit", "5c68402c-2a8d-4776-9237-16349fc72648"),
        ("rolebinding", "1b20d0b9-96a0-42a6-b196-293bb86e62e8"),
    ],
)
@patch("mora.app.AMQPSystem.publish_message")
async def test_refresh_mutators(
    mock: AsyncMock, graphapi_post: GraphAPIPost, model: str, filter_uuid: str
) -> None:
    """Test refresh mutators."""
    mutator = f"{model}_refresh"
    mutation = f"""
      mutation RefreshMutation($uuid: UUID!) {{
        {mutator}(filter: {{uuids: [$uuid]}}) {{
          objects
        }}
      }}
    """
    response = graphapi_post(mutation, variables=dict(uuid=filter_uuid))
    assert response.errors is None
    assert response.data[mutator]["objects"] == [filter_uuid]
    mock.assert_awaited_once_with(routing_key=model, payload=filter_uuid, exchange=None)
