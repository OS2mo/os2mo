#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import exceptions
from mora import lora
from mora import settings
from mora import util as mora_util

from . import util


@util.mock()
@freezegun.freeze_time('2010-06-01', tz_offset=2)
class Tests(util.TestCase):
    def test_get_date_chunks(self, m):
        def check(validity, dates, expected):
            c = lora.Connector(validity=validity)

            actual = [
                (start.isoformat(), end.isoformat())
                for start, end in c.get_date_chunks(
                    map(mora_util.parsedatetime, dates),
                )
            ]

            self.assertEqual(expected, actual)

        dates = [
            '2010-01-01',
            '2010-05-31',
            '2010-06-01',
            '2010-06-01T12:00:00',
            '2010-06-02',
            '2010-06-03',
            '2011-01-01',
        ]

        with self.subTest('prerequisite'):
            self.assertEqual('2010-06-01T02:00:00+02:00',
                             mora_util.now().isoformat())

        with self.subTest('present I'):
            check('present', dates, [
                ('2010-06-01T00:00:00+02:00', '2010-06-01T12:00:00+02:00'),
            ])

        with self.subTest('past I'):
            check('past', dates, [
                ('2010-01-01T00:00:00+01:00', '2010-05-31T00:00:00+02:00'),
                ('2010-05-31T00:00:00+02:00', '2010-06-01T00:00:00+02:00'),
            ])

        with self.subTest('future I'):
            check('future', dates, [
                ('2010-06-01T12:00:00+02:00', '2010-06-02T00:00:00+02:00'),
                ('2010-06-02T00:00:00+02:00', '2010-06-03T00:00:00+02:00'),
                ('2010-06-03T00:00:00+02:00', '2011-01-01T00:00:00+01:00'),
            ])

        dates = [
            '2010-05-31',
            '2010-06-01',
            '2010-06-02',
            '2010-06-03',
        ]

        with self.subTest('present I'):
            check('present', dates, [
                ('2010-06-01T00:00:00+02:00', '2010-06-02T00:00:00+02:00'),
            ])

        with self.subTest('past I'):
            check('past', dates, [
                ('2010-05-31T00:00:00+02:00', '2010-06-01T00:00:00+02:00'),
            ])

        with self.subTest('future I'):
            check('future', dates, [
                ('2010-06-02T00:00:00+02:00', '2010-06-03T00:00:00+02:00'),
            ])

        with self.subTest('null'):
            check('past', [], [])
            check('present', [], [])
            check('future', [], [])

        with self.subTest('failing'):
            with self.assertRaises(exceptions.HTTPException):
                check('kaflaflibob', [], [])

    def test_get_effects(self, m):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2010-06-01T02%3A00%3A00%2B02%3A00'
            '&virkningtil=infinity&konsolider=True'
        )
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
                                for t1, t2, v in [
                                    ('01-01-1950', '01-01-2100', 'Aktiv'),
                                    ('01-01-2100', '01-01-2300', 'Inaktiv'),
                                    ('01-01-2300', '01-01-2500', 'Aktiv'),
                                    ('01-01-2500', '01-01-2700', 'Inaktiv'),
                                    ('01-01-2700', '01-01-2900', 'Aktiv'),
                                    ('01-01-2900', '01-01-3100', 'Inaktiv'),
                                    ('01-01-3100', '01-01-3300', 'Aktiv'),
                                ]
                            ]
                        },
                    }]
                }]]
            },
        )

        c = lora.Connector(validity='future')

        self.assertEqual(
            [
                (
                    "2100-01-01 00:00:00+01:00",
                    "2300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2100-01-01T00:00:00+01:00",
                                        "to": "2300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2300-01-01 00:00:00+01:00",
                    "2500-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2300-01-01T00:00:00+01:00",
                                        "to": "2500-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2500-01-01 00:00:00+01:00",
                    "2700-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2500-01-01T00:00:00+01:00",
                                        "to": "2700-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2700-01-01 00:00:00+01:00",
                    "2900-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2700-01-01T00:00:00+01:00",
                                        "to": "2900-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2900-01-01 00:00:00+01:00",
                    "3100-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2900-01-01T00:00:00+01:00",
                                        "to": "3100-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "3100-01-01 00:00:00+01:00",
                    "3300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "3100-01-01T00:00:00+01:00",
                                        "to": "3300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                )
            ],
            [
                (str(start), str(end), entry)
                for start, end, entry in
                c.organisationenhed.get_effects(
                    '00000000-0000-0000-0000-000000000000',
                    relevant={
                        'tilstande': (
                            'organisationenhedgyldighed',
                        ),
                    },
                )
            ],
        )

    def test_errors(self, m):
        for status_in, status_out, error_key in (
            (400, 400, 'E_INVALID_INPUT'),
            (401, 401, 'E_UNAUTHORIZED'),
            (403, 403, 'E_FORBIDDEN'),
            (426, 500, 'E_UNKNOWN'),
            (500, 500, 'E_UNKNOWN'),
        ):
            with self.subTest('{} - json'.format(status_in)):
                m.get(
                    'http://mox/organisation/organisationenhed?uuid=42',
                    json={
                        "message": "go away",
                    },
                    status_code=status_in,
                )

                with self.assertRaises(exceptions.HTTPException) as ctxt:
                    lora.organisationenhed.get('42')

                self.assertEqual(
                    {
                        'error': True,
                        'status': status_out,
                        'error_key': error_key,
                        'description': 'go away',
                    },
                    ctxt.exception.response.json,
                )

            with self.subTest('{} - text'.format(status_in)):
                m.get(
                    'http://mox/organisation/organisationenhed?uuid=42',
                    text="I hate you",
                    status_code=status_in,
                )

                with self.assertRaises(exceptions.HTTPException) as ctxt:
                    lora.organisationenhed.get('42')

                self.assertEqual(
                    {
                        'error': True,
                        'status': status_out,
                        'error_key': error_key,
                        'description': 'I hate you',
                    },
                    ctxt.exception.response.json,
                )

    @util.override_app_config(DEBUG=True)
    def test_error_debug(self, m):
        m.get(
            'http://mox/organisation/organisationenhed?uuid=42',
            json={
                "message": "go away",
                "something": "other",
            },
            status_code=500,
        )

        with self.assertRaises(exceptions.HTTPException) as ctxt:
            lora.organisationenhed.get('42')

        self.assertEqual(
            {
                'error': True,
                'status': 500,
                'error_key': 'E_UNKNOWN',
                'description': 'go away',
                'context': {
                    'message': 'go away',
                    'something': 'other',
                },
            },
            ctxt.exception.response.json,
        )

    def test_finding_nothing(self, m):
        m.get(
            'http://mox/organisation/organisationenhed?uuid=42',
            json={
                'results': []
            },
        )

        self.assertIsNone(lora.organisationenhed.get('42'))

        m.get(
            'http://mox/organisation/organisationenhed?uuid=42',
            json={
                'results': []
            },
        )

        self.assertIsNone(lora.organisationenhed.get('42'))

    @freezegun.freeze_time('2001-01-01', tz_offset=1)
    def test_get_effects_2(self, m):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2001-01-01T01%3A00%3A00%2B01%3A00'
            '&virkningtil=infinity&konsolider=True'
        )
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
                                for t1, t2, v in [
                                    ('01-01-1950', '01-01-2100', 'Aktiv'),
                                    ('01-01-2100', '01-01-2300', 'Inaktiv'),
                                    ('01-01-2300', '01-01-2500', 'Aktiv'),
                                    ('01-01-2500', '01-01-2700', 'Inaktiv'),
                                    ('01-01-2700', '01-01-2900', 'Aktiv'),
                                    ('01-01-2900', '01-01-3100', 'Inaktiv'),
                                    ('01-01-3100', '01-01-3300', 'Aktiv'),
                                ]
                            ]
                        },
                    }]
                }]]
            },
        )

        c = lora.Connector(validity='future')

        self.assertEqual(
            [
                (
                    "2100-01-01 00:00:00+01:00",
                    "2300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2100-01-01T00:00:00+01:00",
                                        "to": "2300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2300-01-01 00:00:00+01:00",
                    "2500-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2300-01-01T00:00:00+01:00",
                                        "to": "2500-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2500-01-01 00:00:00+01:00",
                    "2700-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2500-01-01T00:00:00+01:00",
                                        "to": "2700-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2700-01-01 00:00:00+01:00",
                    "2900-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2700-01-01T00:00:00+01:00",
                                        "to": "2900-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2900-01-01 00:00:00+01:00",
                    "3100-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2900-01-01T00:00:00+01:00",
                                        "to": "3100-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "3100-01-01 00:00:00+01:00",
                    "3300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "3100-01-01T00:00:00+01:00",
                                        "to": "3300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                )
            ],
            [
                (str(start), str(end), entry)
                for start, end, entry in
                c.organisationenhed.get_effects(
                    '00000000-0000-0000-0000-000000000000',
                    relevant={
                        'tilstande': (
                            'organisationenhedgyldighed',
                        ),
                    },
                )
            ],
        )
