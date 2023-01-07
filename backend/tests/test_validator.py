# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json

import pytest
import respx
from httpx import Response

from mora import lora
from mora import util as mora_util
from mora.service.validation import validator


async def test_startdate_should_be_smaller_than_enddate() -> None:
    assert not (
        await validator._is_date_range_valid(
            None, "01-01-2017", "01-01-2016", None, "whatever"
        )
    )


@pytest.mark.parametrize(
    "expect,validities",
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
    ],
)
@pytest.mark.usefixtures("mock_asgi_transport")
@respx.mock
async def test_validity_ranges(
    expect: bool, validities: list[tuple[str, str, str]]
) -> None:
    url = "http://localhost/lora/organisation/organisationenhed"
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
    route = respx.get(url).mock(Response(200, json=payload))

    assert expect is (
        await validator._is_date_range_valid(
            "00000000-0000-0000-0000-000000000000",
            mora_util.parsedatetime("01-01-2000"),
            mora_util.parsedatetime("01-01-3000"),
            c,
            "organisationenhedgyldighed",
        )
    )

    assert json.loads(route.calls[0].request.read()) == {
        "uuid": ["00000000-0000-0000-0000-000000000000"],
        "virkningfra": "2000-01-01T00:00:00+01:00",
        "virkningtil": "3000-01-01T00:00:00+01:00",
        "konsolider": "True",
    }
