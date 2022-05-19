# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import locale
from asyncio import create_task
from asyncio import gather
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from parameterized import parameterized

import tests.cases
from mora import common
from mora.service.facet import get_one_facet


# Old list_facets implementation
async def list_facets(orgid: UUID):
    orgid = str(orgid)

    c = common.get_connector()

    async def transform(facet_tuple):
        facetid, facet = facet_tuple
        return await get_one_facet(c, facetid, orgid, facet)

    response = await c.facet.get_all(ansvarlig=orgid, publiceret="Publiceret")
    response = await gather(
        *[create_task(transform(facet_tuple)) for facet_tuple in response]
    )

    return sorted(
        response,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f["name"]) if f.get("name") else "",
    )


@pytest.mark.usefixtures("sample_structures_no_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@patch("mora.conf_db.get_configuration", new=lambda *x: {})
class Tests(tests.cases.AsyncLoRATestCase):
    maxDiff = None

    @classmethod
    def get_lora_environ(cls):
        # force LoRA to run under a UTC timezone, ensuring that we
        # handle this case correctly for reading
        return {
            "TZ": "UTC",
        }

    @parameterized.expand(
        [
            [UUID("456362c4-0ee4-4e5e-a72c-751239745e62")],
            [UUID("00000000-0000-0000-0000-000000000000")],
        ]
    )
    async def test_list_facet_equivalence(
        self,
        uuid: UUID,
    ):
        url = f"/service/o/{str(uuid)}/f/"
        expected = await list_facets(uuid)
        await self.assertRequestResponse(url, expected)
