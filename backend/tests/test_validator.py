# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime
import unittest
import json

import freezegun
import respx
import tests.cases
from mora import config
from mora import lora
from mora import util as mora_util
from mora.service.validation import validator
from parameterized import parameterized
from httpx import Response


class AsyncTestIsDateRangeValid(tests.cases.AsyncLoRATestCase):
    async def test_startdate_should_be_smaller_than_enddate(self):
        self.assertFalse(
            await validator._is_date_range_valid(
                None, "01-01-2017", "01-01-2016", None, "whatever"
            )
        )

    @parameterized.expand(
        [
            # just valid
            (True, [("-infinity", "infinity", "Aktiv")]),
            # exact coverage
            (True, [("01-01-2000", "01-01-3000", "Aktiv")]),
            # multiple sequences, but valid
            (
                True,
                [
                    ("01-01-1940", "01-01-1950", "Inaktiv"),
                    ("01-01-1950", "01-01-2100", "Aktiv"),
                    ("01-01-2100", "01-01-2300", "Aktiv"),
                    ("01-01-2300", "01-01-2500", "Aktiv"),
                    ("01-01-2500", "01-01-2700", "Aktiv"),
                    ("01-01-2700", "01-01-2900", "Aktiv"),
                    ("01-01-2900", "01-01-3100", "Aktiv"),
                    ("01-01-3100", "01-01-3300", "Inaktiv"),
                ],
            ),
            # valid sequences, with gaps outside active period.
            (
                True,
                [
                    ("01-01-1960", "01-01-1980", "Aktiv"),
                    ("01-01-2000", "01-01-3000", "Aktiv"),
                ],
            ),
            # no validity
            (False, []),
            # completely invalid
            (False, [("-infinity", "infinity", "Inaktiv")]),
            # no complete coverage
            (False, [("01-01-2000", "01-01-2100", "Aktiv")]),
            # there's a hole in the middle
            (
                False,
                [
                    ("01-01-2000", "01-01-2250", "Aktiv"),
                    ("01-01-2750", "infinity", "Aktiv"),
                ],
            ),
            # there's an invalidity in the middle
            (
                False,
                [
                    ("01-01-2000", "01-01-2250", "Aktiv"),
                    ("01-01-2250", "01-01-2750", "Inaktiv"),
                    ("01-01-2750", "infinity", "Aktiv"),
                ],
            ),
            # starts too late!
            (False, [("01-01-2500", "infinity", "Aktiv")]),
            # ends too soon!
            (False, [("01-01-1930", "01-01-2500", "Aktiv")]),
        ]
    )
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    @respx.mock
    async def test_validity_ranges(self, expect, validities):
        settings = config.get_settings()
        url = f"{settings.lora_url}organisation/organisationenhed"
        c = lora.Connector(
            virkningfra="2000-01-01", virkningtil="3000-01-01"
        ).organisationenhed

        payload = {
            "results": [
                [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "registreringer": [
                            {
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
                                                "to_included": False,
                                            },
                                        }
                                        for t1, t2, v in validities
                                    ]
                                },
                            }
                        ],
                    }
                ]
            ]
        }
        route = respx.get(
            url,
        ).mock(Response(200, json=payload))

        self.assertIs(
            expect,
            await validator._is_date_range_valid(
                "00000000-0000-0000-0000-000000000000",
                mora_util.parsedatetime("01-01-2000"),
                mora_util.parsedatetime("01-01-3000"),
                c,
                "organisationenhedgyldighed",
            ),
        )

        self.assertEqual(
            json.loads(route.calls[0].request.read()),
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2000-01-01T00:00:00+01:00",
                "virkningtil": "3000-01-01T00:00:00+01:00",
                "konsolider": "True",
            },
        )


class TestGetEndpointDate(unittest.TestCase):
    def setUp(self):
        self.org_unit = {
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+00",
                            "from_included": True,
                            "to": "2017-08-29 00:00:00+00",
                            "to_included": False,
                        },
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "-infinity",
                            "from_included": True,
                            "to": "2017-01-01 00:00:00+00",
                            "to_included": False,
                        },
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from": "2017-08-29 00:00:00+00",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ]
            }
        }
        self.enddate = datetime.datetime(
            2017,
            8,
            29,
            0,
            0,
            0,
            tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
        )
        self.startdate = datetime.datetime(
            2017,
            1,
            1,
            0,
            0,
            0,
            tzinfo=datetime.timezone(datetime.timedelta(0), "+00:00"),
        )
