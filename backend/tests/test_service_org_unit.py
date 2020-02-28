# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import json

import freezegun
import requests_mock
from mock import patch

from tests import util


class TestAddressLookup(util.TestCase):
    @freezegun.freeze_time('2018-03-15')
    @util.mock()
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
            '&virkningfra=-infinity',
            json={
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
