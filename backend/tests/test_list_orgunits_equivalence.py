import pytest
import freezegun

import tests
from parameterized import parameterized
import urllib

from uuid import UUID
from typing import Optional
from typing import Union
from typing import List
from datetime import date
from datetime import datetime
from itertools import product

from more_itertools import unzip

from mora import common
from mora.service.orgunit import get_details_from_query_args
from mora.service.orgunit import get_one_orgunit
from mora import mapping


async def list_orgunits(
    orgid: UUID,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    query: Optional[str] = None,
    root: Optional[str] = None,
    hierarchy_uuids: Optional[List[UUID]] = None,
    only_primary_uuid: Optional[bool] = None,
    # TODO: Handle at
    at: Optional[Union[date, datetime]] = None,
    details: Optional[str] = None,
):
    orgid = str(orgid)
    c = common.get_connector()

    kwargs = dict(
        limit=limit,
        start=start,
        tilhoerer=orgid,
        gyldighed="Aktiv",
    )

    if query:
        kwargs.update(vilkaarligattr="%{}%".format(query))
    if hierarchy_uuids:
        kwargs["opmærkning"] = [str(uuid) for uuid in hierarchy_uuids]

    uuid_filters = []
    if root:
        enheder = await c.organisationenhed.get_all()

        uuids, enheder = unzip(enheder)
        # Fetch parent_uuid from objects
        parent_uuids = map(mapping.PARENT_FIELD.get_uuid, enheder)
        # Create map from uuid --> parent_uuid
        parent_map = dict(zip(uuids, parent_uuids))

        def entry_under_root(uuid):
            """Check whether the given uuid is in the subtree under 'root'.

            Works by recursively ascending the parent_map.

            If the specified root is found, we must have started in its subtree.
            If the specified root is not found, we will stop searching at the
                root of the organisation tree.
            """
            if uuid not in parent_map:
                return False
            return uuid == root or entry_under_root(parent_map[uuid])

        uuid_filters.append(entry_under_root)

    details = get_details_from_query_args({"details": details})

    async def get_minimal_orgunit(*args, **kwargs):
        return await get_one_orgunit(
            *args, details=details, only_primary_uuid=only_primary_uuid, **kwargs
        )

    search_result = await c.organisationenhed.paged_get(
        get_minimal_orgunit, uuid_filters=uuid_filters, **kwargs
    )
    return search_result


org_uuids = [
    UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
    UUID("00000000-0000-0000-0000-000000000000"),
]
ostart = [None, 0, 2]
olimit = [None, 0, 5]
query = [None, "Teknisk", "Kommune"]
root = [None, "2665d8e0-435b-5bb6-a550-f275692984ef", "23a2ace2-52ca-458d-bead-d1a42080579f"]
hierarchy_uuids = [None, [UUID("00000000-0000-0000-0000-000000000000")]]
only_primary = [None, False, True]
at = [None]
details = [None, "minimal", "nchildren", "self", "full", "path"]
param_tests = list(
    product(org_uuids, ostart, olimit, query, root, hierarchy_uuids, only_primary, at, details)
)


@pytest.mark.equivalence
@pytest.mark.usefixtures("sample_structures_no_reset")
class Tests(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(param_tests)
    async def test_list_orgunits_equivalence(
        self,
        org_uuid: UUID,
        start: Optional[int],
        limit: Optional[int],
        query: Optional[str],
        root: Optional[str],
        hierarchy_uuids: Optional[List[UUID]],
        only_primary_uuid: Optional[bool],
        at: Optional[str],
        details: Optional[str],
    ):
        query_args = {}
        if start is not None:
            query_args["start"] = start
        if limit is not None:
            query_args["limit"] = limit
        if query is not None:
            query_args["query"] = query
        if root is not None:
            query_args["root"] = root
        if hierarchy_uuids is not None:
            query_args["hierarchy_uuids"] = hierarchy_uuids
        if only_primary_uuid is not None:
            query_args["only_primary_uuid"] = only_primary_uuid
        if at is not None:
            query_args["at"] = at
        if details is not None:
            query_args["details"] = details

        print(org_uuid)
        print(query_args)

        url_parameters = ""
        if query_args:
            url_parameters += "?" + urllib.parse.urlencode(query_args, True)

        url = f"/service/o/{org_uuid}/ou/" + url_parameters
        expected = await list_orgunits(org_uuid, **query_args)
        print("OLD")
        import json
        print(json.dumps(expected, indent=4))
        await self.assertRequestResponse(url, expected)
