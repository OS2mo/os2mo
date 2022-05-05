#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from mora.common import create_organisationsenhed_payload

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestCreateOrgEnhedPayload:
    def test_create_organisationenhed(self):

        payload = create_organisationsenhed_payload(
            enhedsnavn="enhedsnavn",
            valid_from="2016-01-01T00:00:00+01:00",
            valid_to="2018-01-01T00:00:00+01:00",
            brugervendtnoegle="brugervendtnoegle",
            tilhoerer="e0f7a6f7-2a76-45dc-b326-d49b4bb2c2b9",
            enhedstype="28d3c9f6-cce0-4649-bf73-ccbb78dc04e4",
            overordnet="47145ce1-c702-42c2-a88e-011eb09d250f",
        )
        assert payload == {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "enhedsnavn": "enhedsnavn",
                        "brugervendtnoegle": "brugervendtnoegle",
                        "virkning": {
                            "from": "2016-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00",
                        },
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "overordnet": [
                    {
                        "uuid": "47145ce1-c702-42c2-a88e-011eb09d250f",
                        "virkning": {
                            "from": "2016-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00",
                        },
                    }
                ],
                "tilhoerer": [
                    {
                        "uuid": "e0f7a6f7-2a76-45dc-b326-d49b4bb2c2b9",
                        "virkning": {
                            "from": "2016-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00",
                        },
                    }
                ],
                "enhedstype": [
                    {
                        "uuid": "28d3c9f6-cce0-4649-bf73-ccbb78dc04e4",
                        "virkning": {
                            "from": "2016-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00",
                        },
                    }
                ],
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "virkning": {
                            "from": "2016-01-01T00:00:00+01:00",
                            "to": "2018-01-01T00:00:00+01:00",
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
        }
