# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest

import tests.cases
from mora import lora


@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class AsyncTests(tests.cases.AsyncLoRATestCase):
    maxDiff = None

    async def test_create_engagement(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "primary": {"uuid": "d60d1fd6-e561-463c-9a43-2fa99d27c7a3"},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "user_key": "1234",
                "fraction": 10,
                "extension_1": "test1",
                "extension_7": "test7",
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        (engagementid,) = await self.assertRequest(
            "/service/details/create",
            json=payload,
            amqp_topics={
                "employee.engagement.create": 1,
                "org_unit.engagement.create": 1,
            },
        )

        expected = {
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "primær": [
                    {
                        "uuid": "d60d1fd6-e561-463c-9a43-2fa99d27c7a3",
                        "virkning": {
                            "from": "2017-12-01 00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 00:00:00+01",
                            "to_included": False,
                        },
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": "1234",
                        "funktionsnavn": "Engagement",
                    }
                ],
                "organisationfunktionudvidelser": [
                    {
                        "fraktion": 10,
                        "udvidelse_1": "test1",
                        "udvidelse_7": "test7",
                        "virkning": {
                            "from": "2017-12-01 " "00:00:00+01",
                            "from_included": True,
                            "to": "2017-12-02 " "00:00:00+01",
                            "to_included": False,
                        },
                    }
                ],
            },
        }

        actual_engagement = await c.organisationfunktion.get(engagementid)

        self.assertRegistrationsEqual(actual_engagement, expected)

    async def test_create_engagement_from_unit(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
        unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

        payload = [
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": unitid},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"
        with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
            (engagementid,) = await self.assertRequest(
                "/service/details/create",
                json=payload,
                amqp_topics={
                    "employee.engagement.create": 1,
                    "org_unit.engagement.create": 1,
                },
            )

        expected = {
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": userid,
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": unitid,
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Engagement",
                    }
                ]
            },
        }

        actual_engagement = await c.organisationfunktion.get(engagementid)

        self.assertRegistrationsEqual(actual_engagement, expected)

    async def test_create_engagement_no_valid_to(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"

        payload = [
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                },
            }
        ]

        with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
            (engagementid,) = await self.assertRequest(
                "/service/details/create",
                json=payload,
                amqp_topics={
                    "employee.engagement.create": 1,
                    "org_unit.engagement.create": 1,
                },
            )

        expected = {
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Engagement",
                    }
                ]
            },
        }

        actual_engagement = await c.organisationfunktion.get(engagementid)

        self.assertRegistrationsEqual(actual_engagement, expected)

    async def test_create_engagement_no_job_function(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"

        payload = [
            {
                "type": "engagement",
                "person": {"uuid": userid},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
            (engagementid,) = await self.assertRequest(
                "/service/details/create",
                json=payload,
                amqp_topics={
                    "employee.engagement.create": 1,
                    "org_unit.engagement.create": 1,
                },
            )

        expected = {
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01",
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Engagement",
                    }
                ]
            },
        }

        actual_engagement = await c.organisationfunktion.get(engagementid)

        self.assertRegistrationsEqual(expected, actual_engagement)

    async def test_edit_engagement_no_overwrite(self):
        # Check the POST request

        engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"

        req = [
            {
                "type": "engagement",
                "uuid": engagement_uuid,
                "data": {
                    "primary": {"uuid": "cdb026cc-dea9-45e9-98b3-0ccf50537ce4"},
                    "fraction": 30,
                    "extension_7": "test7",
                    "org_unit": {"uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"},
                    "user_key": "regnormsberiger",
                    "job_function": {"uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                    "engagement_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            }
        ]

        await self.assertRequestResponse(
            "/service/details/edit",
            [engagement_uuid],
            json=req,
            amqp_topics={
                "employee.engagement.update": 1,
                "org_unit.engagement.update": 1,
            },
        )

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                    {
                        "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                ],
                "primær": [
                    {
                        "uuid": "cdb026cc-dea9-45e9-98b3-0ccf50537ce4",
                        "virkning": {
                            "from": "2018-04-01 00:00:00+02",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement",
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                        "brugervendtnoegle": "regnormsberiger",
                        "funktionsnavn": "Engagement",
                    },
                ],
                "organisationfunktionudvidelser": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                        "udvidelse_1": "test1",
                        "udvidelse_2": "test2",
                        "udvidelse_9": "test9",
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                        "fraktion": 30,
                        "udvidelse_1": "test1",
                        "udvidelse_2": "test2",
                        "udvidelse_7": "test7",
                        "udvidelse_9": "test9",
                    },
                ],
            },
        }

        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual_engagement = await c.organisationfunktion.get(engagement_uuid)

        self.assertRegistrationsEqual(expected_engagement, actual_engagement)

    async def test_edit_engagement_overwrite(self):
        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"

        req = [
            {
                "type": "engagement",
                "uuid": engagement_uuid,
                "original": {
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                    "person": {"uuid": userid},
                    "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "job_function": {"uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
                    "engagement_type": {"uuid": "32547559-cfc1-4d97-94c6-70b192eff825"},
                },
                "data": {
                    "job_function": {"uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                    "engagement_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            }
        ]

        await self.assertRequestResponse(
            "/service/details/edit",
            [engagement_uuid],
            json=req,
            amqp_topics={
                "employee.engagement.update": 1,
                "org_unit.engagement.update": 1,
            },
        )

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                    {
                        "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        },
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        },
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement",
                    }
                ],
                "organisationfunktionudvidelser": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                        "udvidelse_1": "test1",
                        "udvidelse_2": "test2",
                        "udvidelse_9": "test9",
                    },
                ],
            },
        }

        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual_engagement = await c.organisationfunktion.get(engagement_uuid)

        self.assertRegistrationsEqual(expected_engagement, actual_engagement)

    async def test_terminate_engagement_via_employee(self):
        # Check the POST request
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {"validity": {"to": "2017-11-30"}}

        await self.assertRequestResponse(
            f"/service/e/{userid}/terminate",
            userid,
            json=payload,
            amqp_topics={
                "employee.employee.delete": 1,
                "employee.address.delete": 1,
                "employee.association.delete": 1,
                "employee.engagement.delete": 1,
                "employee.it.delete": 1,
                "employee.leave.delete": 1,
                "employee.manager.delete": 1,
                "employee.role.delete": 1,
                "org_unit.association.delete": 1,
                "org_unit.engagement.delete": 1,
                "org_unit.manager.delete": 1,
                "org_unit.role.delete": 1,
            },
        )

        expected = {
            "note": "Afsluttet",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01",
                        },
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity",
                        },
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity",
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement",
                    }
                ],
                "organisationfunktionudvidelser": [
                    {
                        "udvidelse_1": "test1",
                        "udvidelse_2": "test2",
                        "udvidelse_9": "test9",
                        "virkning": {
                            "from": "2017-01-01 " "00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    }
                ],
            },
        }

        engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"

        actual_engagement = await c.organisationfunktion.get(engagement_uuid)

        self.assertRegistrationsEqual(expected, actual_engagement)


@pytest.mark.usefixtures("load_fixture_data_with_reset")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Tests(tests.cases.LoRATestCase):
    maxDiff = None

    def test_create_engagement_fails_on_empty_payload(self):
        payload = [
            {
                "type": "engagement",
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Missing org_unit",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "org_unit",
                "obj": payload[0],
                "status": 400,
            },
            json=payload,
            status_code=400,
        )

    def test_edit_engagement_fails_on_invalid_payloads(self):
        payload = {
            "type": "engagement",
            "uuid": "00000000-0000-0000-0000-000000000000",
        }

        self.assertRequestResponse(
            "/service/details/edit",
            {
                "description": "Missing data",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "status": 400,
                "key": "data",
                "obj": {
                    "type": "engagement",
                    "uuid": "00000000-0000-0000-0000-000000000000",
                },
            },
            json=payload,
            status_code=400,
        )

    def test_create_engagement_fails_on_missing_unit(self):
        # Check the POST request
        payload = [
            {
                "type": "engagement",
                "person": {"uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "org_unit": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Org unit not found.",
                "error": True,
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
            json=payload,
            status_code=404,
        )

    def test_create_engagement_fails_on_missing_person(self):
        # Check the POST request
        payload = [
            {
                "type": "engagement",
                "person": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "User not found.",
                "error": True,
                "error_key": "E_USER_NOT_FOUND",
                "employee_uuid": "00000000-0000-0000-0000-000000000000",
                "status": 404,
            },
            json=payload,
            status_code=404,
        )

    def test_terminate_engagement_with_both_from_and_to_date(self):
        # Terminate engagement for Anders And employed at humanistisk fak
        employee_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"

        payload = {
            "type": "engagement",
            "uuid": engagement_uuid,
            "validity": {"from": "2018-10-22", "to": "2018-10-25"},
        }

        self.assertRequest("/service/details/terminate", json=payload)

        # Assert termination request is persisted correctly in the past
        r = self.request(
            f"/service/e/{employee_uuid}/details/engagement"
            f"?validity=past&at=2021-10-08"
        )
        assert {"from": "2017-01-01", "to": "2018-10-21"} == r.json()[0]["validity"]

        # Assert termination request is persisted correctly in the present
        r = self.request(
            f"/service/e/{employee_uuid}/details/engagement"
            f"?validity=present&at=2021-10-08"
        )
        assert {"from": "2018-10-26", "to": None} == r.json()[0]["validity"]

    def test_reading_engagement_only_primary_uuid(self):
        actual = self.assertRequest(
            "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
            "/details/engagement?only_primary_uuid=1",
        )[0]

        engagement_type = actual.get("engagement_type")
        job_function = actual.get("job_function")
        org_unit = actual.get("org_unit")
        person = actual.get("person")

        self.assertListEqual(list(engagement_type.keys()), ["uuid"])
        self.assertListEqual(list(job_function.keys()), ["uuid"])
        self.assertListEqual(list(org_unit.keys()), ["uuid"])
        self.assertListEqual(list(person.keys()), ["uuid"])

    def test_reading_engagement_calculate_primary(self):
        r = self.assertRequest(
            "/service/e/236e0a78-11a0-4ed9-8545-6286bb8611c7"
            "/details/engagement?calculate_primary=1"
        )

        assert r[0]["is_primary"] is False
        assert r[1]["is_primary"] is True
