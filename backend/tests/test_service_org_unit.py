# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
from asyncio import Future
from contextlib import nullcontext as does_not_raise
from unittest.mock import call
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from os2mo_http_trigger_protocol import MOTriggerRegister
from starlette.datastructures import ImmutableMultiDict

import tests.cases
from mora import lora
from mora import mapping
from mora.config import Settings
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import _get_count_related
from mora.service.orgunit import get_one_orgunit
from mora.service.orgunit import get_unit_ancestor_tree
from mora.service.orgunit import UnitDetails
from mora.triggers import Trigger
from mora.triggers.internal.http_trigger import HTTPTriggerException
from mora.triggers.internal.http_trigger import register
from tests import util
from tests.util import sample_structures_minimal_cls_fixture


@pytest.mark.usefixtures("mock_asgi_transport")
@freezegun.freeze_time("2018-03-15")
@respx.mock
def test_unit_past(service_client: TestClient) -> None:
    unitid = "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc"

    reg = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": "IDR\u00c6TSPARK",
                    "enhedsnavn": "Ballerup Idr\u00e6tspark",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ]
        },
        "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
        "fratidspunkt": {
            "graenseindikator": True,
            "tidsstempeldatotid": "2018-03-09T14:38:45.310653+01:00",
        },
        "livscykluskode": "Rettet",
        "relationer": {
            "adresser": [
                {
                    "objekttype": "a8c8fe66-2ab1-46ed-ba99-ed05e855d65f",
                    "uuid": "9ab45e95-a42a-47c0-b284-e5d2377fc429",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "objekttype": "80764a2f-6a7b-492c-92d9-96d24ac845ea",
                    "urn": "urn:mailto:tbri@balk.dk",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "enhedstype": [
                {
                    "uuid": "547e6946-abdb-4dc2-ad99-b6042e05a7e4",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "9f42976b-93be-4e0b-9a25-0dcb8af2f6b4",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilhoerer": [
                {
                    "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilknyttedeenheder": [
                {
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    }
                }
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "gyldighed": "Inaktiv",
                    "virkning": {
                        "from": "-infinity",
                        "from_included": True,
                        "to": "1993-01-01 00:00:00+01",
                        "to_included": False,
                    },
                },
            ]
        },
        "tiltidspunkt": {"tidsstempeldatotid": "infinity"},
    }

    url = "http://localhost/lora/organisation/organisationenhed"
    route = respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    [
                        {
                            "id": "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc",
                            "registreringer": [
                                reg,
                            ],
                        }
                    ]
                ]
            },
        )
    )

    mo_url = f"/service/ou/{unitid}/details/org_unit?validity=past"
    respx.get(mo_url).pass_through()

    with util.patch_query_args({"validity": "past"}):
        response = service_client.get(mo_url)
        assert response.status_code == 200
        assert response.json() == []

    assert json.loads(route.calls[0].request.read()) == {
        "uuid": [unitid],
        "virkningfra": "-infinity",
        "virkningtil": "2018-03-15T00:00:00+01:00",
        "konsolider": "True",
    }


@pytest.fixture
def t_sender_mock():
    with patch(
        "mora.triggers.internal.http_trigger.http_sender", new_callable=util.CopyingMock
    ) as mock:
        yield mock


@pytest.fixture
def t_fetch_mock():
    with patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger") as mock:
        yield mock


@pytest.fixture
def load_org_mock():
    with patch("mora.graphapi.versions.latest.org_unit.load_org_unit") as mock:
        yield mock


async def test_returns_integration_error_on_wrong_status(
    service_client: TestClient, load_org_mock, t_sender_mock, t_fetch_mock
):
    with util.override_config(Settings(http_endpoints=["http://whatever"])):
        t_fetch_mock.return_value = [
            MOTriggerRegister(
                **{
                    "event_type": mapping.EventType.ON_BEFORE,
                    "request_type": mapping.RequestType.REFRESH,
                    "role_type": "org_unit",
                    "url": "/triggers/ou/refresh",
                }
            )
        ]
        Trigger.registry = {}
        await register(None)
        t_fetch_mock.assert_called()

    error_msg = "Something horrible happened"
    response_future = Future()
    response_future.set_exception(HTTPTriggerException(error_msg))
    t_sender_mock.side_effect = response_future

    load_org_mock.return_value.objects = [{}]
    response = service_client.get(
        "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh"
    )
    assert response.status_code == 400
    result = response.json()
    assert "INTEGRATION_ERROR" in result.get("error_key")
    assert error_msg in result.get("description")

    t_sender_mock.assert_called_with(
        "http://whatever/triggers/ou/refresh",
        {
            "request_type": mapping.RequestType.REFRESH,
            "request": {"uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4"},
            "role_type": "org_unit",
            "event_type": mapping.EventType.ON_BEFORE,
            "org_unit_uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4",
            "uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4",
        },
        timeout=5,
    )


async def test_returns_message_on_success(
    service_client: TestClient, load_org_mock, t_sender_mock, t_fetch_mock
):
    with util.override_config(Settings(http_endpoints=["http://whatever"])):
        t_fetch_mock.return_value = [
            MOTriggerRegister(
                **{
                    "event_type": mapping.EventType.ON_BEFORE,
                    "request_type": mapping.RequestType.REFRESH,
                    "role_type": "org_unit",
                    "url": "/triggers/ou/refresh",
                }
            )
        ]
        Trigger.registry = {}
        await register(None)
        t_fetch_mock.assert_called()

    response_msg = "Something good happened"
    response_future = Future()
    response_future.set_result(response_msg)
    t_sender_mock.return_value = response_future

    load_org_mock.return_value.objects = [{}]

    response = service_client.get(
        "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh"
    )
    assert response.status_code == 200
    result = response.json()
    assert response_msg == result["message"]

    t_sender_mock.assert_has_calls(
        [
            call(
                "http://whatever/triggers/ou/refresh",
                {
                    "request_type": mapping.RequestType.REFRESH,
                    "request": {"uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4"},
                    "role_type": "org_unit",
                    "event_type": mapping.EventType.ON_BEFORE,
                    "org_unit_uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4",
                    "uuid": "44c86c7a-cfe0-447e-9706-33821b5721a4",
                },
                timeout=5,
            )
        ]
    )


def test_returns_404_on_unknown_unit(service_client: TestClient) -> None:
    with patch("mora.graphapi.versions.latest.org_unit.load_org_unit") as mock:
        mock.return_value.objects = []

        response = service_client.get(
            "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh"
        )
        assert response.status_code == 404
        result = response.json()
        assert "NOT_FOUND" in result.get("error_key")


@sample_structures_minimal_cls_fixture
class AsyncTestGetOneOrgUnit(tests.cases.AsyncLoRATestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self._connector = lora.Connector(
            virkningfra="-infinity", virkningtil="infinity"
        )
        self._orgunit_uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    @util.patch_query_args()
    async def test_get_one_orgunit_with_association_count(self):
        result = await get_one_orgunit(
            self._connector,
            self._orgunit_uuid,
            count_related={"association": AssociationReader},
        )
        assert "association_count" in result

    @util.patch_query_args()
    async def test_details_nchildren(self):
        await self._assert_orgunit_keys(
            {"uuid", "name", "user_key", "validity", "child_count"},
            details=UnitDetails.NCHILDREN,
        )

    @util.patch_query_args()
    async def test_details_path(self):
        await self._assert_orgunit_keys(
            {"uuid", "name", "user_key", "validity", "location"},
            details=UnitDetails.PATH,
        )

    async def _assert_orgunit_keys(self, expected_keys, **kwargs):
        orgunit = await get_one_orgunit(self._connector, self._orgunit_uuid, **kwargs)
        self.assertSetEqual(set(orgunit.keys()), expected_keys)


@pytest.mark.parametrize(
    "arguments, value, expected_raise",
    [
        # Testing valid name.
        ({"count": "association"}, {"association"}, does_not_raise()),
        # Testing valid name repeated.
        (
            [("count", "association"), ("count", "association")],
            {"association"},
            does_not_raise(),
        ),
        # Testing multiple valid names.
        (
            [("count", "association"), ("count", "engagement")],
            {"association", "engagement"},
            does_not_raise(),
        ),
        # Testing invalid name with HTTP Exception raise.
        (
            [("count", "association"), ("count", "foobar")],
            None,
            pytest.raises(HTTPException),
        ),
    ],
)
def test_valid_name(arguments, value, expected_raise):
    with expected_raise:
        with util.patch_query_args(ImmutableMultiDict(arguments)):
            assert value == _get_count_related()


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestGetUnitAncestorTree(tests.cases.AsyncLoRATestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self._connector = lora.Connector(
            virkningfra="-infinity", virkningtil="infinity"
        )
        # The OU "Humanistisk Fakultet" has 3 engagements and 1 association.
        # We need the UUID of a *child* OU to test `get_unit_ancestor_tree`.
        # Below is the UUID of "Filosofisk Institut".
        self._orgunit_uuid = [UUID("9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")]

    async def test_count_association(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "association"})):
            result = await get_unit_ancestor_tree(
                self._orgunit_uuid, only_primary_uuid=False
            )
            self._assert_matching_ou_has(
                result,
                user_key="hum",
                association_count=1,
            )

    async def test_count_engagement(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "engagement"})):
            result = await get_unit_ancestor_tree(
                self._orgunit_uuid, only_primary_uuid=False
            )
            self._assert_matching_ou_has(
                result,
                user_key="hum",
                engagement_count=3,
            )

    def _assert_matching_ou_has(self, doc, user_key=None, **attrs):
        # Recurse into `doc` until we find a dictionary whose `user_key` equals
        # `user_key`. Then, assert that each key-value pair in `attrs` is
        # present in the matching dict, and has the expected value.
        def visit(node):
            if isinstance(node, list):
                for ou in node:
                    visit(ou)
            elif isinstance(node, dict):
                if "children" in node:
                    for ou in node["children"]:
                        visit(ou)
                if node.get("user_key") == user_key:
                    for attr_name, attr_value in attrs.items():
                        assert node.get(attr_name) == attr_value

        visit(doc)
