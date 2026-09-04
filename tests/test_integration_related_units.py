# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

HUM = {
    "org_unit": [
        {
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ],
    "uuid": "5c68402c-2a8d-4776-9237-16349fc72648",
    "user_key": "rod <-> hum",
    "validity": {
        "from": "2016-06-01",
        "to": None,
    },
}

HIST = {
    "org_unit": [
        {
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        },
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ],
    "uuid": "daa77a4d-6500-483d-b099-2c2eb7fa7a76",
    "user_key": "rod <-> fil",
    "validity": {
        "from": "2017-01-01",
        "to": "2018-12-31",
    },
}


def pf(
    url: str,
    json: dict,
    status_code: int,
    overrides: dict,
    freeze_time: str | None,
):
    """A parametrize case that freezes the whole test at `freeze_time`."""
    return pytest.param(
        url,
        json,
        status_code,
        overrides,
        freeze_time,
        marks=pytest.mark.freeze_time(freeze_time or "2017-06-01"),
    )
