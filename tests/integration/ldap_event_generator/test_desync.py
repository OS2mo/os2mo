# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import sleep
from collections.abc import Awaitable
from collections.abc import Callable
from datetime import timedelta
from functools import partial
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastramqpi.context import Context
from more_itertools import one

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.ldap_event_generator import _generate_events
from mo_ldap_import_export.ldap_event_generator import _poll
from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import AddLdapPerson
from tests.integration.conftest import DNList2UUID


@pytest.fixture
def search_base() -> str:
    settings = Settings()
    ldap_ou_to_search_in = one(settings.ldap_ous_to_search_in)
    return combine_dn_strings([ldap_ou_to_search_in, settings.ldap_search_base])


@pytest.fixture
def generate_events(
    context: Context, search_base: str
) -> Callable[[], Awaitable[set[UUID]]]:
    dataloader = context["user_context"]["dataloader"]
    sessionmaker = context["sessionmaker"]

    seeded_poller = partial(
        _poll,
        ldap_connection=dataloader.ldapapi.ldap_connection,
        search_base=search_base,
        ldap_unique_id_field=Settings().ldap_unique_id_field,
    )

    async def inner() -> set[UUID]:
        # This uses AsyncMock to collect UUIDs that are send out,
        # as we cannot easily list all UUIDs on a queue in RabbitMQ.
        ldap_amqpsystem = AsyncMock()
        await _generate_events(
            ldap_amqpsystem, search_base, sessionmaker, seeded_poller
        )
        call_args = [call.args for call in ldap_amqpsystem.method_calls]
        return {uuid for routing_key, uuid in call_args}

    return inner


@pytest.mark.integration_test
@pytest.mark.envvar({"LISTEN_TO_CHANGES_IN_LDAP": "False"})
@pytest.mark.parametrize(
    "",
    [
        # Integration time is far behind LDAP time
        pytest.param(
            marks=pytest.mark.freeze_time(
                timedelta(days=-1), tick=True, real_asyncio=True
            )
        ),
        # Integration time is very close to LDAP time
        pytest.param(
            marks=pytest.mark.freeze_time(
                timedelta(days=0), tick=True, real_asyncio=True
            )
        ),
        # Integration time is far ahead of LDAP time
        pytest.param(
            marks=pytest.mark.freeze_time(
                timedelta(days=1), tick=True, real_asyncio=True
            )
        ),
    ],
)
@pytest.mark.usefixtures("test_client")
async def test_no_desync(
    ldap_org_uuid: UUID,
    add_ldap_person: AddLdapPerson,
    generate_events: Callable[[], Awaitable[set[UUID]]],
    dnlist2uuid: DNList2UUID,
) -> None:
    # This checks from the start of the universe till now
    # We expect there to be only our ldap org
    results = await generate_events()
    assert results == {ldap_org_uuid}

    # Sleep for one second to to ensure our person is not created in same second as
    # the ldap org. This is required since our timestamps are truncated to suport AD.
    await sleep(1)
    ldap_person_uuid = await dnlist2uuid(await add_ldap_person("abk", "0101901234"))
    assert ldap_person_uuid is not None

    # This checks from 1 second ago till now, we expect "ldap_org_uuid" to appear again,
    # since we are starting at the second it was in (truncating).
    results = await generate_events()
    assert results == {ldap_org_uuid, ldap_person_uuid}

    # We wait another second and check again. We know expect "ldap_org_uuid" to have
    # disappeared, since we are 2 seconds / truncations away, however "ldap_person_uuid"
    # should still appear, since we are within its truncated second.
    await sleep(1)
    results = await generate_events()
    assert results == {ldap_person_uuid}
