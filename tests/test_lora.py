#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import lora
from mora import settings
from mora import util as mora_util

from . import util


@util.mock()
@freezegun.freeze_time('2010-06-01')
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

        with self.subTest('present I'):
            check('present', dates, [
                ('2010-06-01T00:00:00+02:00', '2010-06-01T12:00:00+02:00'),
                ('2010-06-01T12:00:00+02:00', '2010-06-02T00:00:00+02:00'),
            ])

        with self.subTest('past I'):
            check('past', dates, [
                ('2010-01-01T00:00:00+01:00', '2010-05-31T00:00:00+02:00'),
                ('2010-05-31T00:00:00+02:00', '2010-06-01T00:00:00+02:00'),
            ])

        with self.subTest('future I'):
            check('future', dates, [
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
            with self.assertRaises(ValueError):
                check('kaflaflibob', [], [])

    def test_get_effects(self, m):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2010-06-02T00%3A00%3A00%2B02%3A00'
            '&virkningtil=infinity'
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
                                    ('01-01-1900', '01-01-2100', 'Aktiv'),
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
