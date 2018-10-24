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
            '&virkningtil=2016-06-06T00%3A00%3A00.000001%2B02%3A00',
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
                'error': True,
                'error_key': 'E_NO_LOCAL_MUNICIPALITY',
                'description': 'No local municipality found.',
                'status': 400,
            },
            status_code=400,
        )

    @freezegun.freeze_time('2016-06-06')
    @util.mock()
    def test_autocomplete_invalid_municipality(self, mock):
        mock.get(
            'http://mox/organisation/organisation'
            '?uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2016-06-06T00%3A00%3A00%2B02%3A00'
            '&virkningtil=2016-06-06T00%3A00%3A00.000001%2B02%3A00',
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
                'error': True,
                'error_key': 'E_NO_LOCAL_MUNICIPALITY',
                'description': 'No local municipality found.',
                'status': 400,
            },
            status_code=400,
        )

    @freezegun.freeze_time('2017-07-28')
    @util.mock(('reading-organisation.json', 'dawa-autocomplete.json'))
    def test_autocomplete(self, mock):
        found = [
            {
                "location": {
                    "name": "Strandlodsvej 25M, 1. th, 2300 K\u00f8benhavn S",
                    "uuid": "b18f681b-dcce-4a1f-9231-08182653dbd9"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 1. tv, 2300 K\u00f8benhavn S",
                    "uuid": "21483493-bf6d-4cdd-badd-74bc5109c7b1"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 2. th, 2300 K\u00f8benhavn S",
                    "uuid": "22bf4e3e-14f3-4096-b479-2e8d4ac090fb"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 2. tv, 2300 K\u00f8benhavn S",
                    "uuid": "d4764afd-f5f1-4038-9298-9148bcb56421"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 3. th, 2300 K\u00f8benhavn S",
                    "uuid": "13deac37-805b-4024-a6dc-4b5f6808571c"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 3. tv, 2300 K\u00f8benhavn S",
                    "uuid": "2bd96c7d-e9b5-449b-889c-f09a4c1fae50"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 4. th, 2300 K\u00f8benhavn S",
                    "uuid": "c5871526-6f4f-425c-bd3f-05b837df24cb"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 4. tv, 2300 K\u00f8benhavn S",
                    "uuid": "6ee8b42e-bfc2-42d3-974f-47791c99b375"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 5. th, 2300 K\u00f8benhavn S",
                    "uuid": "fd3fceb2-860a-4c15-b57f-795cbfda5882"
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 5. tv, 2300 K\u00f8benhavn S",
                    "uuid": "8aa7e68d-e451-43c7-9c02-705ea7a9bb40"
                }
            }
        ]

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=Strandlodsvej+25M&global=1',
            found,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=Strandlodsvej+25M&global=true',
            found,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=Strandlodsvej+25M',
            [],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=Strandlodsvej+25M&global=0',
            [],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
            'address_autocomplete/?q=Strandlodsvej+25M&global=false',
            [],
        )
