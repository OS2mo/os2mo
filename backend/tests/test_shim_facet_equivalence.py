# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import locale
import urllib
from asyncio import create_task
from asyncio import gather
from itertools import product
from typing import Optional
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from parameterized import parameterized

import tests.cases
from mora import common
from mora.service.facet import get_classes_under_facet
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


# Old get_all_classes implementation
async def get_all_classes(
    facet: str,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    only_primary_uuid: Optional[bool] = None,
):
    return await get_classes_under_facet(
        None, facet, only_primary_uuid=only_primary_uuid, start=start, limit=limit
    )


facet_names = [
    "association_type",
    "ef71fe9c-7901-48e2-86d8-84116e210202",
]
ostart = [None, 0, 2]
olimit = [None, 0, 5]
obools = [None, False, True]
get_all_classes_param_tests = list(product(facet_names, ostart, olimit, obools))


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

    @parameterized.expand(get_all_classes_param_tests)
    async def test_get_all_classes_equivalence(
        self,
        facet: str,
        start: Optional[int],
        limit: Optional[int],
        only_primary_uuid: Optional[bool],
    ):
        query_args = {}
        if start is not None:
            query_args["start"] = start
        if limit is not None:
            query_args["limit"] = limit
        if only_primary_uuid is not None:
            query_args["only_primary_uuid"] = only_primary_uuid

        url_parameters = ""
        if query_args:
            url_parameters += "?" + urllib.parse.urlencode(query_args)

        url = f"/service/f/{facet}/" + url_parameters
        expected = await get_all_classes(facet, **query_args)
        await self.assertRequestResponse(url, expected)
