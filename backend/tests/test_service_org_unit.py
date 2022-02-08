# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import Future
from uuid import UUID

import freezegun
import pytest
from mora.service import orgunit
import tests.cases
from unittest.mock import MagicMock
from mock import call
from mock import patch
from mora import lora
from mora import mapping
from mora.config import Settings
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import _get_count_related
from mora.service.orgunit import get_children
from mora.service.orgunit import get_one_orgunit
from mora.service.orgunit import get_orgunit
from mora.service.orgunit import get_unit_ancestor_tree
from mora.service.orgunit import UnitDetails
from mora.triggers import Trigger
from mora.triggers.internal.http_trigger import HTTPTriggerException
from mora.triggers.internal.http_trigger import register
from more_itertools import one
from os2mo_http_trigger_protocol import MOTriggerRegister
from starlette.datastructures import ImmutableMultiDict
from tests import util
from yarl import URL
from mora.triggers.internal import http_trigger


class TestAddressLookup(tests.cases.TestCase):
    @freezegun.freeze_time("2018-03-15")
    @util.MockAioresponses()
    def test_unit_past(self, mock):
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

        url = URL("http://mox/organisation/organisationenhed")
        mock.get(
            url,
            payload={
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

        with util.patch_query_args({"validity": "past"}):
            self.assertRequestResponse(
                "/service/ou/" + unitid + "/details/org_unit?validity=past",
                [],
            )

        call_args = one(mock.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": [unitid],
                "virkningfra": "-infinity",
                "virkningtil": "2018-03-15T00:00:00+01:00",
                "konsolider": "True",
            },
        )


# TODO: MagicMock() er nok ikke vejen frem
@pytest.fixture()
def trigger_fetch_endpoint_trigger(monkeypatch):
    # called = MagicMock()
    # monkeypatch.setattr(http_trigger, "fetch_endpoint_trigger", called)
    with patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger"):
        yield


# TODO: Fix!
@pytest.fixture()
def trigger_http_sender(monkeypatch):
    # called = MagicMock()
    # monkeypatch.setattr(http_trigger, "http_sender")
    with patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger"):
        yield


# TODO: Fix!
@pytest.fixture()
def trigger_get_one_orgunit(monkeypatch):
    called = MagicMock()
    monkeypatch.setattr(orgunit, "get_one_orgunit", called)
    # with patch("mora.service.orgunit.get_one_orgunit"):
    yield


class AsyncTestTriggerExternalIntegration(tests.cases.AsyncTestCase):
    @util.override_config(Settings(http_endpoints=["http://whatever"]))
    async def test_returns_integration_error_on_wrong_status(self):
        async def mock_fetch(*args, **kwargs):
            return [
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
        print(await register(None))
        assert False
        t_fetch_mock.assert_called()

        error_msg = "Something horrible happened"
        response_future = Future()
        response_future.set_exception(HTTPTriggerException(error_msg))
        t_sender_mock.side_effect = response_future

        mock.return_value = {"whatever": 123}
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

    @util.override_config(Settings(http_endpoints=["http://whatever"]))
    @patch("mora.triggers.internal.http_trigger.fetch_endpoint_trigger")
    @patch(
        "mora.triggers.internal.http_trigger.http_sender", new_callable=util.CopyingMock
    )
    @patch("mora.service.orgunit.get_one_orgunit")
    async def test_returns_message_on_success(self, mock, t_sender_mock, t_fetch_mock):
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

        mock.return_value = {"whatever": 123}
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


class TestTriggerExternalIntegration(tests.cases.TestCase):
    @patch("mora.service.orgunit.get_one_orgunit")
    def test_returns_404_on_unknown_unit(self, mock):
        mock.return_value = {}

        r = self.assertRequest(
            "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh", status_code=404
        )
        self.assertIn("NOT_FOUND", r.get("error_key"))


class AsyncTestGetOneOrgUnit(tests.cases.AsyncLoRATestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.load_sample_structures(minimal=True)
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


class TestGetOrgUnit(tests.cases.AsyncConfigTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.load_sample_structures()
        # The OU "Humanistisk Fakultet" has 3 engagements and 1 association.
        self._orgunit_uuid = UUID("9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")

    async def test_count_association(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "association"})):
            result = await get_orgunit(self._orgunit_uuid)
            self.assertEqual(result["association_count"], 1)

    async def test_count_engagement(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "engagement"})):
            result = await get_orgunit(self._orgunit_uuid)
            self.assertEqual(result["engagement_count"], 3)


class TestGetChildren(tests.cases.AsyncConfigTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.load_sample_structures()
        self._connector = lora.Connector(
            virkningfra="-infinity", virkningtil="infinity"
        )
        # The OU "Humanistisk Fakultet" has 3 engagements and 1 association.
        # We need the UUID of a *parent* OU to test `get_children`.
        # Below is the UUID of "Overordnet Enhed".
        self._orgunit_uuid = UUID("9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")

    async def test_count_association(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "association"})):
            result = await get_children("ou", self._orgunit_uuid)
            self._assert_matching_ou_has(
                result,
                user_key="hum",
                association_count=1,
            )

    async def test_count_engagement(self):
        with util.patch_query_args(ImmutableMultiDict({"count": "engagement"})):
            result = await get_children("ou", self._orgunit_uuid)
            self._assert_matching_ou_has(
                result,
                user_key="hum",
                engagement_count=3,
            )

    def _assert_matching_ou_has(self, doc, user_key=None, **attrs):
        for node in doc:
            if node.get("user_key") == user_key:
                for attr_name, attr_value in attrs.items():
                    self.assertEqual(node.get(attr_name), attr_value)


class TestGetUnitAncestorTree(tests.cases.AsyncConfigTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.load_sample_structures()
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
