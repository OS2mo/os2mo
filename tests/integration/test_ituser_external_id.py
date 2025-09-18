# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID
from uuid import uuid4

import pytest

from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.models import Engagement
from mo_ldap_import_export.models import ITUser
from mo_ldap_import_export.utils import MO_TZ


@pytest.mark.integration_test
async def test_create_ituser_read_equivalence(
    mo_api: MOAPI,
    mo_person: UUID,
    adtitle: UUID,
) -> None:
    ituser_uuid = uuid4()
    ituser = ITUser(
        uuid=ituser_uuid,
        user_key="ava",
        itsystem=adtitle,
        person=mo_person,
        validity={"from": datetime(1970, 1, 1, tzinfo=MO_TZ)},
    )
    await mo_api.create([ituser])
    assert await mo_api.load_mo_it_user(ituser_uuid) == ituser

    ituser = ituser.copy(update={"user_key": "modified"})
    await mo_api.edit([ituser])
    assert await mo_api.load_mo_it_user(ituser_uuid) == ituser


@pytest.mark.integration_test
async def test_create_ituser_external_id_read_equivalence(
    mo_api: MOAPI,
    mo_person: UUID,
    adtitle: UUID,
) -> None:
    ituser_uuid = uuid4()
    ituser = ITUser(
        uuid=ituser_uuid,
        user_key="ava",
        itsystem=adtitle,
        person=mo_person,
        external_id="my_external_id",
        validity={"from": datetime(1970, 1, 1, tzinfo=MO_TZ)},
    )
    await mo_api.create([ituser])
    assert await mo_api.load_mo_it_user(ituser_uuid) == ituser

    ituser = ituser.copy(update={"external_id": "modified"})
    await mo_api.edit([ituser])
    assert await mo_api.load_mo_it_user(ituser_uuid) == ituser


@pytest.mark.integration_test
async def test_create_ituser_engagements_read_equivalence(
    mo_api: MOAPI,
    mo_person: UUID,
    adtitle: UUID,
    mo_org_unit: UUID,
    ansat: UUID,
    jurist: UUID,
    primary: UUID,
) -> None:
    engagement_uuid = uuid4()
    engagement = Engagement(
        uuid=engagement_uuid,
        user_key="engagement",
        person=mo_person,
        org_unit=mo_org_unit,
        engagement_type=ansat,
        job_function=jurist,
        primary=primary,
        validity={"from": datetime(1970, 1, 1, tzinfo=MO_TZ)},
    )
    await mo_api.create([engagement])

    ituser_uuid = uuid4()
    ituser = ITUser(
        uuid=ituser_uuid,
        user_key="ava",
        itsystem=adtitle,
        person=mo_person,
        engagements=[engagement_uuid],
        validity={"from": datetime(1970, 1, 1, tzinfo=MO_TZ)},
    )
    await mo_api.create([ituser])
    mo_ituser = await mo_api.load_mo_it_user(ituser_uuid)
    assert mo_ituser is not None
    assert mo_ituser == ituser

    ituser = ituser.copy(update={"engagements": []})
    await mo_api.edit([ituser])
    mo_ituser = await mo_api.load_mo_it_user(ituser_uuid)
    assert mo_ituser is not None
    assert mo_ituser == ituser
