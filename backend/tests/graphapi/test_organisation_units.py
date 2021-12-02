#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from itertools import compress
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
from aioresponses import CallbackResult
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import unzip
from pytest import MonkeyPatch
from ramodels.mo import OrganisationUnitRead
from yarl import URL

import mora.graphapi.dataloaders as dataloaders
from .util import execute


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestOrganisationUnitsQuery:
    """Class collecting organisation unit query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(OrganisationUnitRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all our organisation units."""

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    org_units {
                        name user_key validity {from to}
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["org_units"] == [
            {
                "name": org_unit["name"],
                "user_key": org_unit["user_key"],
                "validity": org_unit["validity"],
            }
            for org_unit in test_data
        ]

    @given(test_data=st.lists(st.builds(OrganisationUnitRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test, patch_loader):
        """Test that we can query organisation units by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        org_units(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response = graphapi_test.post(
                "/graphql", json={"query": query, "variables": {"uuids": test_uuids}}
            )

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None

        # Check UUID equivalence
        result_uuids = [ou.get("uuid") for ou in data["org_units"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))


# This is kept to check parent/children loaders


def gen_organisation_unit(
    uuid: Optional[UUID] = None,
    user_key: str = "user_key",
    name: str = "name",
    parent_uuid: Optional[UUID] = None,
    from_time: str = "1970-01-01 00:00:00+01",
) -> Dict[str, Any]:
    uuid = uuid or uuid4()
    virkning = {"from": from_time, "to": "infinity"}
    organisation_unit = {
        "id": str(uuid),
        "registreringer": [
            {
                "attributter": {
                    "organisationenhedegenskaber": [
                        {
                            "brugervendtnoegle": user_key,
                            "enhedsnavn": name,
                            "virkning": virkning,
                        }
                    ],
                },
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {"gyldighed": "Aktiv", "virkning": virkning}
                    ]
                },
                "relationer": {
                    "overordnet": [
                        {
                            "uuid": str(parent_uuid) if parent_uuid else None,
                            "virkning": virkning,
                        }
                    ],
                },
            }
        ],
    }
    return organisation_unit


def mock_organisation_unit(aioresponses, *args, **kwargs) -> UUID:
    organisation_unit = gen_organisation_unit()

    aioresponses.get(
        URL("http://mox/organisation/organisationenhed"),
        payload={"results": [[organisation_unit]]},
        repeat=True,
    )

    return organisation_unit["id"]


def get_children_uuids(parent_map, parent_uuid):
    uuids, parent_uuids = unzip(parent_map.items())
    matching_tuples = map(lambda uuid: uuid == parent_uuid, parent_uuids)
    children_uuids = compress(uuids, matching_tuples)
    return list(children_uuids)


def setup_organisation_tree(aioresponses):
    # Organisation Unit Tree:
    #
    # org_unit1
    # ├── org_unit11
    # │   ├── org_unit111
    # │   └── org_unit112
    # └── org_unit12
    #     ├── org_unit121
    #     └── org_unit122
    #         └── org_unit1221
    org_unit1 = gen_organisation_unit()
    org_unit11 = gen_organisation_unit(parent_uuid=org_unit1["id"])
    org_unit12 = gen_organisation_unit(parent_uuid=org_unit1["id"])
    org_unit111 = gen_organisation_unit(parent_uuid=org_unit11["id"])
    org_unit112 = gen_organisation_unit(parent_uuid=org_unit11["id"])
    org_unit121 = gen_organisation_unit(parent_uuid=org_unit12["id"])
    org_unit122 = gen_organisation_unit(parent_uuid=org_unit12["id"])
    org_unit1221 = gen_organisation_unit(parent_uuid=org_unit122["id"])
    organisation_units = [
        org_unit1,
        org_unit11,
        org_unit12,
        org_unit111,
        org_unit112,
        org_unit121,
        org_unit122,
        org_unit1221,
    ]
    organisation_unit_map = {
        organisation_unit["id"]: organisation_unit
        for organisation_unit in organisation_units
    }

    def get_parent_uuid(uuid):
        organisation_unit = organisation_unit_map[uuid]
        relationer = organisation_unit["registreringer"][0]["relationer"]
        return relationer["overordnet"][0]["uuid"]

    parent_map = {
        organisation_unit["id"]: get_parent_uuid(organisation_unit["id"])
        for organisation_unit in organisation_units
    }

    def callback(url, json, **kwargs):
        matching_org_units = [organisation_units]
        overordnet = json.get("overordnet")
        uuids = json.get("uuid")
        if overordnet:
            overordnet_uuid = overordnet
            children_uuids = get_children_uuids(parent_map, overordnet_uuid)
            matching_org_units = list(map(organisation_unit_map.get, children_uuids))
        elif uuids:
            matching_org_units = list(map(organisation_unit_map.get, uuids))
        return CallbackResult(status=200, payload={"results": [matching_org_units]})

    aioresponses.get(
        URL("http://mox/organisation/organisationenhed"),
        callback=callback,
        repeat=True,
    )

    return organisation_unit_map, parent_map, org_unit1, org_unit1221


@pytest.mark.asyncio
async def test_query_organisation_unit_tree_root(aioresponses):
    """Test that we are able to query parents and children of the root."""
    organisation_unit_map, parent_map, root, _ = setup_organisation_tree(aioresponses)
    uuid = root["id"]

    query = """
        query TestQuery($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
                uuid, parent_uuid, parent { uuid }, children { uuid }
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid)})

    # We expect 2 outgoing request:
    # 1x For the first lookup
    # 1x To lookup children
    # As parent is None, no request is made to look it up
    assert sum(len(v) for v in aioresponses.requests.values()) == 2

    # We expect the root to have exactly two children
    children_uuids = get_children_uuids(parent_map, uuid)
    assert len(children_uuids) == 2

    parent_uuid = parent_map[uuid]
    assert parent_uuid is None

    assert result.errors is None
    assert result.data["org_units"] == [
        {
            "uuid": root["id"],
            "parent_uuid": None,
            "parent": None,
            "children": [{"uuid": uuid} for uuid in children_uuids],
        }
    ]


@pytest.mark.asyncio
async def test_query_organisation_unit_tree_deepest_child(aioresponses):
    """Test that we are able to query parents and children of the deepest child."""
    organisation_unit_map, parent_map, _, deepest_child = setup_organisation_tree(
        aioresponses
    )
    uuid = deepest_child["id"]

    query = """
        query TestQuery($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
                uuid, parent_uuid, parent { uuid }, children { uuid }
            }
        }
    """
    result = await execute(query, {"uuid": str(uuid)})

    # We expect 3 outgoing request:
    # 1x For the first lookup
    # 1x To lookup children
    # 1x To lookup parent
    assert sum(len(v) for v in aioresponses.requests.values()) == 3

    # We expect the deepest child to have zero children
    children_uuids = get_children_uuids(parent_map, uuid)
    assert len(children_uuids) == 0

    parent_uuid = parent_map[uuid]
    assert parent_uuid is not None

    assert result.errors is None
    assert result.data["org_units"] == [
        {
            "uuid": uuid,
            "parent_uuid": parent_uuid,
            "parent": {"uuid": parent_uuid},
            "children": [],
        }
    ]


@pytest.mark.parametrize("num_parents", [0, 1, 2, 3])
@pytest.mark.asyncio
async def test_query_organisation_unit_tree_layers(aioresponses, num_parents):
    """Test that we are able to query multiple levels of parents at once."""
    organisation_unit_map, parent_map, _, deepest_child = setup_organisation_tree(
        aioresponses
    )
    uuid = deepest_child["id"]

    def build_parents_query(levels):
        if levels == 0:
            return "uuid, parent_uuid"
        return "uuid, parent_uuid, parent {" + build_parents_query(levels - 1) + "}"

    parents_snippet = build_parents_query(num_parents)
    query = (
        """
        query TestQuery($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
            """
        + parents_snippet
        + """
            }
        }
    """
    )
    result = await execute(query, {"uuid": str(uuid)})

    # We expect one outgoing request per layer of parents in the query
    assert sum(len(v) for v in aioresponses.requests.values()) == num_parents + 1

    def build_response(uuid, levels):
        parent_uuid = parent_map[uuid]
        if levels == 0:
            return {"uuid": uuid, "parent_uuid": parent_uuid}
        return {
            "uuid": uuid,
            "parent_uuid": parent_uuid,
            "parent": build_response(parent_uuid, levels - 1),
        }

    assert result.errors is None
    assert result.data["org_units"] == [build_response(uuid, num_parents)]
