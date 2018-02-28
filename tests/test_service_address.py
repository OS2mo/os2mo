#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from tests import util


class TestAddressLookup(util.TestCase):
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
            '/service/o/00000000-0000-0000-0000-000000000000/'
            'address_autocomplete/?q=42',
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
            '/service/o/00000000-0000-0000-0000-000000000000/'
            'address_autocomplete/?q=42',
            {
                'message': 'No local municipality found!',
                'status': 404,
            },
            status_code=404,
        )

    @util.mock()
    @freezegun.freeze_time('2016-06-06')
    def test_autocomplete(self, mock):
        mock.get(
            'http://mox/organisation/organisation'
            '?uuid=456362c4-0ee4-4e5e-a72c-751239745e62'
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
                                            "urn": "urn:dk:kommune:751",
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

        mock.get(
            'http://dawa.aws.dk/adresser/autocomplete?'
            'kommunekode=751&noformat=1&q=42',
            json=[{
                "tekst": "Strandlodsvej 25M, 7. tv, 2300 København S",
                "adresse": {
                    "id": "00002732-733c-433a-a5da-a7d428a980cf",
                    "href": "http://dawa.aws.dk/adresser/"
                            "00002732-733c-433a-a5da-a7d428a980cf",
                    "vejnavn": "Strandlodsvej",
                    "husnr": "25M",
                    "etage": "7",
                    "dør": "tv",
                    "supplerendebynavn": None,
                    "postnr": "2300",
                    "postnrnavn": "København S",
                    "stormodtagerpostnr": None,
                    "stormodtagerpostnrnavn": None
                }
            }])

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=42',
            [{
                'location': {
                    'uuid': "00002732-733c-433a-a5da-a7d428a980cf",
                    'name': 'Strandlodsvej 25M, 7. tv, 2300 København S'
                }
            }])

    @freezegun.freeze_time('2016-06-06')
    @util.mock()
    def test_autocomplete_global(self, mock):
        mock.get(
            'http://dawa.aws.dk/adresser/autocomplete?noformat=1&q=42',
            json=[{
                "tekst": "Strandlodsvej 25M, 7. tv, 2300 København S",
                "adresse": {
                    "id": "00002732-733c-433a-a5da-a7d428a980cf",
                    "href": "http://dawa.aws.dk/adresser/"
                            "00002732-733c-433a-a5da-a7d428a980cf",
                    "vejnavn": "Strandlodsvej",
                    "husnr": "25M",
                    "etage": "7",
                    "dør": "tv",
                    "supplerendebynavn": None,
                    "postnr": "2300",
                    "postnrnavn": "København S",
                    "stormodtagerpostnr": None,
                    "stormodtagerpostnrnavn": None
                }
            }])

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=42&global=1',
            [{
                'location': {
                    'uuid': "00002732-733c-433a-a5da-a7d428a980cf",
                    'name': 'Strandlodsvej 25M, 7. tv, 2300 København S'
                }
            }])
