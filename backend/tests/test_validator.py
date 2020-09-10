# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import unittest

import datetime
import freezegun
import requests_mock

from mora import lora
from mora import settings
from mora import util as mora_util
from mora.service.validation import validator
from . import util


class TestIsDateRangeValid(util.TestCase):
    def test_startdate_should_be_smaller_than_enddate(self):
        self.assertFalse(
            validator._is_date_range_valid(None, '01-01-2017', '01-01-2016',
                                           None, 'whatever'))

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_validity_ranges(self):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2000-01-01T00%3A00%3A00%2B01%3A00'
            '&virkningtil=3000-01-01T00%3A00%3A00%2B01%3A00'
            '&konsolider=True'
        )

        c = lora.Connector(virkningfra='2000-01-01',
                           virkningtil='3000-01-01').organisationenhed

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
                        mora_util.parsedatetime('01-01-2000'),
                        mora_util.parsedatetime('01-01-3000'),
                        c,
                        'organisationenhedgyldighed'
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
            ('01-01-1940', '01-01-1950', 'Inaktiv'),
            ('01-01-1950', '01-01-2100', 'Aktiv'),
            ('01-01-2100', '01-01-2300', 'Aktiv'),
            ('01-01-2300', '01-01-2500', 'Aktiv'),
            ('01-01-2500', '01-01-2700', 'Aktiv'),
            ('01-01-2700', '01-01-2900', 'Aktiv'),
            ('01-01-2900', '01-01-3100', 'Aktiv'),
            ('01-01-3100', '01-01-3300', 'Inaktiv'),
        ])

        # valid sequences, with gaps outside active period.
        check(True, [
            ('01-01-1960', '01-01-1980', 'Aktiv'),
            ('01-01-2000', '01-01-3000', 'Aktiv'),
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
            ('01-01-1930', '01-01-2500', 'Aktiv'),
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
