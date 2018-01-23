#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import unittest

import freezegun
import requests_mock

from mora import settings
from mora import validator
from mora import util as mora_util


class TestIsDateRangeValid(unittest.TestCase):
    def test_startdate_should_be_smaller_than_enddate(self):
        self.assertFalse(
            validator._is_date_range_valid(None, '01-01-2017', '01-01-2016'))

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_validity_ranges(self):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2000-01-01T00%3A00%3A00%2B01%3A00'
            '&virkningtil=3000-01-01T00%3A00%3A00%2B01%3A00'
        )

        def check(expect, validities):
            with requests_mock.mock() as m:
                m.get(
                    URL,
                    complete_qs=True,
                    json={
                        "results":
                        [[{
                            "id": "00000000-0000-0000-0000-000000000000",
                            "registreringer": [{
                                "tilstande": {
                                    "organisationenhedgyldighed": [
                                        {
                                            "gyldighed": v,
                                            "virkning": {
                                                "from": mora_util.to_lora_time(
                                                    t1,
                                                ),
                                                "from_included": True,
                                                "to": mora_util.to_lora_time(
                                                    t2,
                                                ),
                                                "to_included": False
                                            }
                                        }
                                        for t1, t2, v in validities
                                    ]
                                },
                            }]
                        }]]
                    },
                )

                self.assertIs(
                    expect,
                    validator._is_date_range_valid(
                        '00000000-0000-0000-0000-000000000000',
                        '01-01-2000',
                        '01-01-3000',
                    )
                )

        # just valid
        check(True, [
            ('-infinity', 'infinity', 'Aktiv'),
        ])

        # exact coverage
        check(True, [
            ('01-01-2000', '01-01-3000', 'Aktiv'),
        ])

        # multiple sequences, but valid
        check(True, [
            ('01-01-1700', '01-01-1900', 'Inaktiv'),
            ('01-01-1900', '01-01-2100', 'Aktiv'),
            ('01-01-2100', '01-01-2300', 'Aktiv'),
            ('01-01-2300', '01-01-2500', 'Aktiv'),
            ('01-01-2500', '01-01-2700', 'Aktiv'),
            ('01-01-2700', '01-01-2900', 'Aktiv'),
            ('01-01-2900', '01-01-3100', 'Aktiv'),
            ('01-01-3100', '01-01-3300', 'Inaktiv'),
        ])

        # no validity
        check(False, [])

        # completely invalid
        check(False, [
            ('-infinity', 'infinity', 'Inaktiv'),
        ])

        # no complete coverage
        check(False, [
            ('01-01-2000', '01-01-2100', 'Aktiv'),
        ])

        # there's a hole in the middle
        check(False, [
            ('01-01-2000', '01-01-2250', 'Aktiv'),
            ('01-01-2750', 'infinity', 'Aktiv'),
        ])

        # there's an invalidity in the middle
        check(False, [
            ('01-01-2000', '01-01-2250', 'Aktiv'),
            ('01-01-2250', '01-01-2750', 'Inaktiv'),
            ('01-01-2750', 'infinity', 'Aktiv'),
        ])

        # starts too late!
        check(False, [
            ('01-01-2500', 'infinity', 'Aktiv'),
        ])

        # ends too soon!
        check(False, [
            ('01-01-1500', '01-01-2500', 'Aktiv'),
        ])


class TestGetEndpointDate(unittest.TestCase):
    def setUp(self):
        self.org_unit = {
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+00",
                            "from_included": True,
                            "to": "2017-08-29 00:00:00+00",
                            "to_included": False
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "-infinity",
                            "from_included": True,
                            "to": "2017-01-01 00:00:00+00",
                            "to_included": False
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "2017-08-29 00:00:00+00",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ]
            }
        }
        self.enddate = datetime.datetime(
            2017, 8, 29, 0, 0, 0,
            tzinfo=datetime.timezone(datetime.timedelta(0), '+00:00'))
        self.startdate = datetime.datetime(
            2017, 1, 1, 0, 0, 0,
            tzinfo=datetime.timezone(datetime.timedelta(0), '+00:00'))

    def test_should_return_2017_08_29(self):
        self.assertEqual(self.enddate,
                         validator._get_org_unit_endpoint_date(self.org_unit))

    def test_should_return_2017_01_01(self):
        self.org_unit['tilstande']['organisationenhedgyldighed'][0][
            'virkning']['from_included'] = False
        self.assertEqual(self.startdate,
                         validator._get_org_unit_endpoint_date(self.org_unit,
                                                               False)
                         )


class TestUpdateLocation(unittest.TestCase):
    def test_should_return_false_if_address_is_missing(self):
        frontend_req = {
            'role-type': 'location',
            'location': ''
        }
        self.assertFalse(validator.is_location_update_valid(frontend_req))

    def test_should_return_true_when_address_and_name_is_set(self):
        frontend_req = {
            'role-type': 'location',
            "location": {
                "UUID_EnhedsAdresse": "0a3f50c3-df6f-32b8-e044-0003ba298018",
                "postdistrikt": "Risskov",
                "postnr": "8240",
                "vejnavn": "Pilevej 3, 8240 Risskov"
            },
            'name': 'name'
        }
        self.assertTrue(validator.is_location_update_valid(frontend_req))

    def test_should_return_false_when_name_is_missing(self):
        frontend_req = {
            'role-type': 'location',
            "location": {
                "UUID_EnhedsAdresse": "0a3f50c3-df6f-32b8-e044-0003ba298018",
                "postdistrikt": "Risskov",
                "postnr": "8240",
                "vejnavn": "Pilevej 3, 8240 Risskov"
            },
            'name': ''
        }
        self.assertFalse(validator.is_location_update_valid(frontend_req))

    def test_should_return_status_200_when_location_not_set(self):
        # The first request made by the frontend when adding a new contact
        # channel. The request is not used by the middleend.

        frontend_req = {
            "name": "Nordre Ringgade 1, 8000 Aarhus C",
            "user-key": "NULL",
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "valid-from": "2014-05-05T19:07:48.577000+00:00",
            "valid-to": "infinity",
            "vejnavn": "Nordre Ringgade 1, 8000 Aarhus C",
            "contact-channels": [
                {
                    "contact-info": "+4587150000",
                    "visibility": {
                        "name": "Må vises eksternt",
                        "user-key": "external",
                        "uuid": "c67d7315-a0a2-4238-a883-f33aa7ddabc2"
                    },
                    "type": {
                        "name": "Telefonnummer",
                        "prefix": "urn:magenta.dk:telefon:",
                        "user-key": "Telephone_number"
                    },
                    "valid-to": "infinity",
                    "valid-from": "-infinity"
                }
            ],
            "person": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "role-type": "contact-channel"
        }
        self.assertTrue(validator.is_location_update_valid(frontend_req))
