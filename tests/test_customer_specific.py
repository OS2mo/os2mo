import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from fastramqpi.context import Context
from gql import gql

from mo_ldap_import_export.customer_specific import CustomerSpecific
from mo_ldap_import_export.customer_specific import HolstebroEngagementUpdate
from mo_ldap_import_export.import_export import SyncTool


@pytest.fixture
def gql_client_v7() -> AsyncMock:
    gql_client_v7 = AsyncMock()
    gql_client_v7.execute.return_value = {
        "engagements": {
            "objects": [{"current": {"uuid": "4b32c233-5fec-4d05-be0a-58bef65d0c06"}}]
        }
    }
    return gql_client_v7


@pytest.fixture
def context(
    dataloader: AsyncMock,
    converter: MagicMock,
    export_checks: AsyncMock,
    settings: MagicMock,
    internal_amqpsystem: MagicMock,
    gql_client_v7: MagicMock,
) -> Context:
    context = Context(
        {
            "user_context": {
                "dataloader": dataloader,
                "converter": converter,
                "export_checks": export_checks,
                "internal_amqpsystem": internal_amqpsystem,
                "settings": settings,
                "gql_client_v7": gql_client_v7,
            }
        }
    )
    return context


async def test_template(sync_tool: SyncTool):
    temp = CustomerSpecific()
    temp.sync_to_ldap()
    list_to_ignore = await asyncio.create_task(
        temp.sync_to_mo(context=sync_tool.context)
    )
    assert list_to_ignore == []


async def test_import_holstebroengagementupdate_objects(context: Context):
    test_user_uuid = uuid4()
    test_job_function_uuid = uuid4()
    test_eng_uuid = uuid4()

    test_mock = AsyncMock()
    test_mock.execute.return_value = {
        "engagements": {"objects": [{"current": {"uuid": str(test_eng_uuid)}}]}
    }

    context["user_context"]["gql_client_v7"] = test_mock

    test_query_set_job_title = gql(
        """
            mutation SetJobtitles($uuid: UUID, $from: DateTime, $job_function: UUID) {
              engagement_update(
                input: {uuid: $uuid,
                        validity: {from: $from},
                        job_function: $job_function}
              ) {
                uuid
              }
            }
            """
    )

    test_object = HolstebroEngagementUpdate.from_simplified_fields(
        user_uuid=test_user_uuid, job_function_uuid=test_job_function_uuid
    )

    await test_object.sync_to_ldap()

    uuids_to_ignore = await (asyncio.create_task(test_object.sync_to_mo(context)))

    test_mock.execute.assert_called_with(
        test_query_set_job_title,
        variable_values=jsonable_encoder(
            {
                "uuid": test_eng_uuid,
                "from": datetime.now().date(),
                "job_function": test_job_function_uuid,
            }
        ),
    )
    assert len(uuids_to_ignore) == 1
    assert uuids_to_ignore
