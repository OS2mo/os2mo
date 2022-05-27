# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
from asyncio import Future
from uuid import UUID

import freezegun
import pytest
import respx
from httpx import Response
from mock import call
from mock import patch
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


class AsyncTestAddressLookup(tests.cases.AsyncTestCase):
    @freezegun.freeze_time("2018-03-15")
    @respx.mock
    async def test_unit_past(self):
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

        url = "http://mox/organisation/organisationenhed"
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

        with util.patch_query_args({"validity": "past"}):
            await self.assertRequestResponse(
                "/service/ou/" + unitid + "/details/org_unit?validity=past",
                [],
            )

        self.assertEqual(
            json.loads(route.calls[0].request.read()),
            {
                "uuid": [unitid],
                "virkningfra": "-infinity",
                "virkningtil": "2018-03-15T00:00:00+01:00",
                "konsolider": "True",
            },
        )


class AsyncTestTriggerExternalIntegration(tests.cases.AsyncTestCase):
    @patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger")
    @patch("mora.triggers.internal.http_trigger.http_sender")
    @patch("mora.graphapi.org_unit.load_org_unit")
    async def test_returns_integration_error_on_wrong_status(
        self, mock, t_sender_mock, t_fetch_mock
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

        mock.return_value.objects = [{}]
        r = await self.assertRequest(
            "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh", status_code=400
        )
        self.assertIn("INTEGRATION_ERROR", r.get("error_key"))
        self.assertIn(error_msg, r.get("description"))

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

    @patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger")
    @patch(
        "mora.triggers.internal.http_trigger.http_sender", new_callable=util.CopyingMock
    )
    @patch("mora.graphapi.org_unit.load_org_unit")
    async def test_returns_message_on_success(self, mock, t_sender_mock, t_fetch_mock):
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

        mock.return_value.objects = [{}]

        r = await self.assertRequest(
            "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh"
        )
        self.assertEqual(response_msg, r["message"])

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

    @patch("mora.graphapi.org_unit.load_org_unit")
    async def test_returns_404_on_unknown_unit(self, mock):
        mock.return_value.objects = []

        r = await self.assertRequest(
            "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh", status_code=404
        )
        self.assertIn("NOT_FOUND", r.get("error_key"))


@pytest.mark.usefixtures("sample_structures_minimal")
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
        self.assertIn("association_count", result)

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


class TestGetCountRelated(tests.cases.TestCase):
    def setUp(self):
        super().setUp()
        self._simple = {"association"}
        self._multiple = {"association", "engagement"}

    def test_valid_name(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "association"})):
            self.assertSetEqual(self._simple, _get_count_related())

    def test_valid_name_repeated(self):
        with util.patch_query_args(
            ImmutableMultiDict([("count", "association"), ("count", "association")])
        ):
            self.assertSetEqual(self._simple, _get_count_related())

    def test_multiple_valid_names(self):
        with util.patch_query_args(
            ImmutableMultiDict([("count", "association"), ("count", "engagement")])
        ):
            self.assertSetEqual(self._multiple, _get_count_related())

    def test_invalid_name(self):
        with util.patch_query_args(
            ImmutableMultiDict([("count", "association"), ("count", "foobar")])
        ):
            with self.assertRaises(HTTPException):
                _get_count_related()


@pytest.mark.usefixtures("sample_structures")
class TestGetUnitAncestorTree(tests.cases.AsyncConfigTestCase):
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
                        self.assertEqual(node.get(attr_name), attr_value)

        visit(doc)
