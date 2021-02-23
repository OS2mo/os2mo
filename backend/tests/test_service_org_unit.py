# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json

import freezegun
import requests_mock

from mock import patch
from mora import lora
from mora.async_util import async_to_sync
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import UnitDetails, _get_count_related, get_one_orgunit
from tests import util


class TestAddressLookup(util.TestCase):
    @freezegun.freeze_time('2018-03-15')
    @util.MockAioresponses()
    def test_unit_past(self, mock):
        unitid = 'ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc'

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
                            "to_included": False
                        }
                    }
                ]
            },
            "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
            "fratidspunkt": {
                "graenseindikator": True,
                "tidsstempeldatotid": "2018-03-09T14:38:45.310653+01:00"
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
                            "to_included": False
                        }
                    },
                    {
                        "objekttype": "80764a2f-6a7b-492c-92d9-96d24ac845ea",
                        "urn": "urn:mailto:tbri@balk.dk",
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "547e6946-abdb-4dc2-ad99-b6042e05a7e4",
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "9f42976b-93be-4e0b-9a25-0dcb8af2f6b4",
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "tilhoerer": [
                    {
                        "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd",
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "1993-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "-infinity",
                            "from_included": True,
                            "to": "1993-01-01 00:00:00+01",
                            "to_included": False
                        }
                    }
                ]
            },
            "tiltidspunkt": {
                "tidsstempeldatotid": "infinity"
            }
        }

        mock.get(
            'http://mox/organisation/organisationenhed'
            '?uuid=' + unitid +
            '&virkningtil=2018-03-15T00%3A00%3A00%2B01%3A00'
            '&virkningfra=-infinity'
            '&konsolider=True',
            payload={
                "results": [
                    [
                        {
                            "id": "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc",
                            "registreringer": [
                                reg,
                            ]
                        }
                    ]
                ]
            }
        )

        self.assertRequestResponse(
            '/service/ou/' + unitid + '/details/org_unit?validity=past',
            [],
        )


class TestTriggerExternalIntegration(util.TestCase):
    @patch('mora.service.orgunit.get_one_orgunit')
    def test_returns_404_on_unknown_unit(self, mock):
        mock.return_value = {}

        r = self.assertRequest(
            '/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/trigger-external',
            status_code=404
        )
        self.assertIn('NOT_FOUND', r.get('error_key'))

    @util.override_config({"external_integration": {"org_unit": "http://whatever/"}})
    @patch('mora.service.orgunit.get_one_orgunit')
    @requests_mock.Mocker()
    def test_returns_integration_error_on_wrong_status(self, mock, r_mock):
        mock.return_value = {'whatever': 123}

        error_msg = "Something bad happened"

        r_mock.post(
            (
                "http://whatever/"
            ),
            text=error_msg,
            status_code=500
        )

        r = self.assertRequest(
            '/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/trigger-external',
            status_code=400
        )
        self.assertIn('INTEGRATION_ERROR', r.get('error_key'))
        self.assertIn(error_msg, r.get('description'))

    @util.override_config({"external_integration": {"org_unit": "http://whatever/"}})
    @patch('mora.service.orgunit.get_one_orgunit')
    @requests_mock.Mocker()
    def test_returns_message_on_success(self, mock, r_mock):
        mock.return_value = {'whatever': 123}

        response_msg = "Something good happened"

        r_mock.post(
            (
                "http://whatever/"
            ),
            text=json.dumps({"output": response_msg}),
            status_code=201
        )

        r = self.assertRequest(
            '/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/trigger-external',
        )
        self.assertIn(response_msg, r['message'])
        self.assertEqual(201, r.get('status_code'))


class TestGetOneOrgUnit(util.LoRATestCase):
    def setUp(self):
        self.load_sample_structures(minimal=True)
        self._connector = lora.Connector(
            virkningfra='-infinity', virkningtil='infinity'
        )
        self._orgunit_uuid = '2874e1dc-85e6-4269-823a-e1125484dfd3'

    def test_details_nchildren(self):
        self._assert_orgunit_keys(
            {'uuid', 'name', 'user_key', 'validity', 'child_count'},
            details=UnitDetails.NCHILDREN,
        )

    def test_details_path(self):
        self._assert_orgunit_keys(
            {'uuid', 'name', 'user_key', 'validity', 'location'},
            details=UnitDetails.PATH,
        )

    def test_get_one_orgunit_with_association_count(self):
        result = async_to_sync(get_one_orgunit)(
            self._connector,
            self._orgunit_uuid,
            count_related={'association': AssociationReader},
        )
        self.assertIn('association_count', result)

    def _assert_orgunit_keys(self, expected_keys, **kwargs):
        orgunit = async_to_sync(get_one_orgunit)(
            self._connector, self._orgunit_uuid, **kwargs
        )
        self.assertSetEqual(set(orgunit.keys()), expected_keys)


class TestGetCountRelated(util.TestCase):
    def setUp(self):
        super().setUp()
        self._simple = {'association'}
        self._multiple = {'association', 'engagement'}

    def test_valid_name(self):
        with self.app.test_request_context('?count=association'):
            self.assertSetEqual(self._simple, _get_count_related())

    def test_valid_name_repeated(self):
        with self.app.test_request_context('?count=association&count=association'):
            self.assertSetEqual(self._simple, _get_count_related())

    def test_multiple_valid_names(self):
        with self.app.test_request_context('?count=association&count=engagement'):
            self.assertSetEqual(self._multiple, _get_count_related())

    def test_invalid_name(self):
        with self.app.test_request_context('?count=association&count=foobar'):
            with self.assertRaises(HTTPException):
                _get_count_related()
