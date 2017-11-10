#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from . import util


class TestSetup(util.TestCase):
    @freezegun.freeze_time('2016-06-06')
    @util.mock()
    def test_autocomplete_no_municipality(self, mock):
        mock.get(
            'http://mox/organisation/organisation'
            '?uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2016-06-06T00%3A00%3A00%2B02%3A00'
            '&virkningtil=2016-06-07T00%3A00%3A00%2B02%3A00',
            json={
                "results": [
                    [{
                        "id": "00000000-0000-0000-0000-000000000000",
                        "registreringer": [
                            {
                                "attributter": {
                                    "organisationegenskaber": [
                                        {
                                            "brugervendtnoegle": "bvn",
                                            "organisationsnavn": "onvn",
                                        }
                                    ]
                                },
                                "tilstande": {
                                    "organisationgyldighed": [
                                        {
                                            "gyldighed": "Aktiv",
                                        }
                                    ]
                                },
                            }
                        ]
                    }]
                ]
            }
        )

        self.assertRequestResponse(
            '/addressws/geographical-location'
            '?vejnavn=42&local=00000000-0000-0000-0000-000000000000',
            {
                'message': 'No local municipality found!',
                'status': 404,
            },
            status_code=404,
        )

    @freezegun.freeze_time('2016-06-06')
    @util.mock()
    def test_autocomplete_invalid_municipality(self, mock):
        mock.get(
            'http://mox/organisation/organisation'
            '?uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2016-06-06T00%3A00%3A00%2B02%3A00'
            '&virkningtil=2016-06-07T00%3A00%3A00%2B02%3A00',
            json={
                "results": [
                    [{
                        "id": "00000000-0000-0000-0000-000000000000",
                        "registreringer": [
                            {
                                "attributter": {
                                    "organisationegenskaber": [
                                        {
                                            "brugervendtnoegle": "bvn",
                                            "organisationsnavn": "onavn",
                                        }
                                    ]
                                },
                                "relationer": {
                                    "myndighed": [
                                        {
                                            "urn": "kaflaflibob",
                                        }
                                    ]
                                },
                                "tilstande": {
                                    "organisationgyldighed": [
                                        {
                                            "gyldighed": "Aktiv",
                                        }
                                    ]
                                },
                            }
                        ]
                    }]
                ]
            }
        )

        self.assertRequestResponse(
            '/addressws/geographical-location'
            '?vejnavn=42&local=00000000-0000-0000-0000-000000000000',
            {
                'message': 'No local municipality found!',
                'status': 404,
            },
            status_code=404,
        )
