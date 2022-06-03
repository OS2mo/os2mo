# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import locale
import urllib
from asyncio import create_task
from asyncio import gather
from itertools import product
from typing import Any
from typing import Dict
from typing import Optional
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from parameterized import parameterized

import tests.cases
from mora import common
from mora.service.facet import fetch_class_children
from mora.service.facet import get_one_class
from mora.service.facet import map_query_args_to_class_details
from mora.service.facet import prepare_class_child


# Old get_class implementation
async def get_class(
    classid: UUID,
    query_args: Optional[Dict[str, Any]] = None,
):
    if query_args is None:
        query_args = {}
    only_primary_uuid = query_args.pop("only_primary_uuid", None)

    classid = str(classid)

    c = common.get_connector()
    class_details = map_query_args_to_class_details(query_args.keys())

    return await get_one_class(
        c, classid, details=class_details, only_primary_uuid=only_primary_uuid
    )


# Old get_all_class_children implementation
async def get_all_class_children(
    classid: UUID, only_primary_uuid: Optional[bool] = None
):
    classid = str(classid)

    c = common.get_connector()

    classes = await fetch_class_children(c, classid)
    classes = await gather(
        *[
            create_task(get_one_class(c, *tup, only_primary_uuid=only_primary_uuid))
            for tup in classes
        ]
    )
    classes = await gather(
        *[create_task(prepare_class_child(c, class_)) for class_ in classes]
    )
    return sorted(
        classes,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f["name"]) if f.get("name") else "",
    )


uuids = [
    UUID("32547559-cfc1-4d97-94c6-70b192eff825"),
    UUID("bf65769c-5227-49b4-97c5-642cfbe41aa1"),
]
obools = [None, False, True]
get_class_param_tests = list(product(uuids, obools, obools, obools, obools))
get_all_class_children_param_tests = list(product(uuids, obools))


@pytest.mark.equivalence
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

    @parameterized.expand(get_class_param_tests)
    async def test_get_class_equivalence(
        self,
        uuid: UUID,
        full_name: Optional[bool],
        facet: Optional[bool],
        top_level_facet: Optional[bool],
        only_primary_uuid: Optional[bool],
    ):
        query_args = {}
        if full_name is not None:
            query_args["full_name"] = full_name
        if facet is not None:
            query_args["facet"] = facet
        if top_level_facet is not None:
            query_args["top_level_facet"] = top_level_facet
        if only_primary_uuid is not None:
            query_args["only_primary_uuid"] = only_primary_uuid

        url_parameters = ""
        if query_args:
            url_parameters += "?" + urllib.parse.urlencode(query_args)

        url = f"/service/c/{str(uuid)}/" + url_parameters
        expected = await get_class(
            uuid, query_args={key: value for key, value in query_args.items() if value}
        )
        await self.assertRequestResponse(url, expected)

    @parameterized.expand(get_all_class_children_param_tests)
    async def test_all_class_children_equivalence(
        self,
        uuid: UUID,
        only_primary_uuid: Optional[bool],
    ):
        query_args = {}
        if only_primary_uuid is not None:
            query_args["only_primary_uuid"] = only_primary_uuid

        url_parameters = ""
        if query_args:
            url_parameters += "?" + urllib.parse.urlencode(query_args)

        url = f"/service/c/{str(uuid)}/children" + url_parameters
        expected = await get_all_class_children(uuid, only_primary_uuid)
        await self.assertRequestResponse(url, expected)
