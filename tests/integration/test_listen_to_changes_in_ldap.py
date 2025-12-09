# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

import pytest
from fastramqpi.context import Context
from fastramqpi.pytest_util import retrying
from sqlalchemy import select

from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.ldap_event_generator import MICROSOFT_EPOCH
from mo_ldap_import_export.ldap_event_generator import LastRun
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import DN2UUID


@pytest.fixture
async def get_last_run(context: Context) -> Callable[[], Awaitable[LastRun | None]]:
    sessionmaker = context["sessionmaker"]

    async def inner() -> LastRun | None:
        async with sessionmaker(expire_on_commit=False) as session, session.begin():
            result = await session.scalar(select(LastRun))
            assert isinstance(result, LastRun | None)
            return result

    return inner


@pytest.mark.integration_test
@pytest.mark.envvar({"LISTEN_TO_CHANGES_IN_LDAP": "False"})
async def test_event_generator_does_not_run_without_listen(
    get_last_run: Callable[[], Awaitable[LastRun | None]],
) -> None:
    assert await get_last_run() is None


@pytest.mark.integration_test
@pytest.mark.envvar({"LISTEN_TO_CHANGES_IN_LDAP": "True"})
async def test_event_generator_runs_with_listen(
    get_last_run: Callable[[], Awaitable[LastRun | None]],
    ldap_api: LDAPAPI,
    ldap_suffix: list[str],
    dn2uuid: DN2UUID,
) -> None:
    last_run = await get_last_run()
    assert last_run is not None
    assert last_run.datetime is not None
    assert last_run.search_base == "o=magenta,dc=magenta,dc=dk"
    assert last_run.datetime == MICROSOFT_EPOCH
    assert last_run.uuids == []

    # Create an entity in LDAP and get its UUID
    o_dn_list = ["o=magenta"] + ldap_suffix
    o_dn = combine_dn_strings(o_dn_list)
    await ldap_api.ldap_connection.ldap_add(
        o_dn,
        object_class=["top", "organization"],
        attributes={"objectClass": ["top", "organization"], "o": "magenta"},
    )
    o_uuid = UUID(str(await dn2uuid(o_dn)))

    # Fetch the modification time of the newly created object
    o_modify_timestamp = await ldap_api.get_attribute_by_dn(o_dn, "modifyTimestamp")

    # Check that the event generator found our newly added organization
    async for attempt in retrying():
        with attempt:
            last_run = await get_last_run()
            assert last_run is not None
            assert last_run.datetime is not None
            assert last_run.search_base == "o=magenta,dc=magenta,dc=dk"
            assert last_run.datetime == o_modify_timestamp
            assert last_run.uuids == [o_uuid]


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": ["givenName", "sn"],
                        "uuid": "{{ employee_uuid or '' }}",  # TODO: why is this required?
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                    }
                }
            }
        ),
    }
)
@pytest.mark.usefixtures("mo_org_unit")
async def test_no_event_handlers_if_no_listen(
    graphql_client: GraphQLClient,
) -> None:
    listeners = await graphql_client.read_event_listeners()
    assert listeners.objects == []
