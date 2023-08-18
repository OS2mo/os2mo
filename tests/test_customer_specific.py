import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastramqpi.context import Context

from mo_ldap_import_export.customer_specific import CustomerSpecific
from mo_ldap_import_export.customer_specific import HolstebroEngagementUpdate
from mo_ldap_import_export.import_export import SyncTool


@pytest.fixture
def context(
    dataloader: AsyncMock,
    converter: MagicMock,
    export_checks: AsyncMock,
    settings: MagicMock,
    internal_amqpsystem: MagicMock,
) -> Context:
    context = Context(
        {
            "user_context": {
                "dataloader": dataloader,
                "converter": converter,
                "export_checks": export_checks,
                "internal_amqpsystem": internal_amqpsystem,
                "settings": settings,
            }
        }
    )
    return context


async def test_template(sync_tool: SyncTool):
    temp = CustomerSpecific()
    await asyncio.gather(temp.sync_to_ldap())
    list_to_ignore = (await asyncio.gather(temp.sync_to_mo(context=sync_tool.context)))[
        0
    ]
    assert list_to_ignore == []


async def test_import_holstebroengagementupdate_objects(context: Context):
    test_user_uuid = uuid4()
    test_job_function_uuid = uuid4()
    test_job_function_fallback_uuid = uuid4()
    test_eng_uuid = uuid4()

    test_mock = AsyncMock()
    test_mock.execute.return_value = {
        "engagements": {"objects": [{"current": {"uuid": str(test_eng_uuid)}}]}
    }

    context["graphql_session"] = test_mock

    test_object = HolstebroEngagementUpdate.from_simplified_fields(
        user_uuid=test_user_uuid,
        job_function_uuid=test_job_function_uuid,
        job_function_fallback_uuid=test_job_function_fallback_uuid,
    )

    await asyncio.gather(test_object.sync_to_ldap())

    jobs = (await asyncio.gather(test_object.sync_to_mo(context)))[0]

    comp = [
        {
            "uuid_to_ignore": str(test_eng_uuid),
            "variable_values": {
                "uuid": str(test_eng_uuid),
                "from": str(datetime.now().date()),
                "job_function": str(test_job_function_uuid),
            },
        }
    ]

    jobs[0].pop("document")

    assert jobs == comp
