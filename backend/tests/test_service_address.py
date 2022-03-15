# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import freezegun
import tests.cases
from aioresponses import CallbackResult
from mora import exceptions
from mora.service import address
from more_itertools import one
from tests import util
from tests.util import dar_loader
from yarl import URL


class AsyncTestAddressLookup(tests.cases.AsyncTestCase):
    async def test_many_addresses(self):
        addresses = {
            "00000000-0000-0000-0000-000000000000": {
                "href": None,
                "name": "Ukendt",
                "value": "00000000-0000-0000-0000-000000000000",
                "value2": None,
            },
            "0a3f507b-6b35-32b8-e044-0003ba298018": {
                "href": "https://www.openstreetmap.org/"
                "?mlon=12.3647784&mlat=55.73404048&zoom=16",
                "name": "Hold-An Vej 7, 2750 Ballerup",
                "value": "0a3f507b-6b35-32b8-e044-0003ba298018",
                "value2": None,
            },
            "0a3f5081-75bf-32b8-e044-0003ba298018": {
                "href": "https://www.openstreetmap.org/"
                "?mlon=11.91321841&mlat=55.62985492&zoom=16",
                "name": "Brobjergvej 9, Abbetved, 4060 Kirke S\u00e5by",
                "value": "0a3f5081-75bf-32b8-e044-0003ba298018",
                "value2": None,
            },
            "0ead9b4d-c615-442d-8447-b328a73b5b39": {
                "href": "https://www.openstreetmap.org/"
                "?mlon=12.57924839&mlat=55.68113676&zoom=16",
                "name": "Pilestr\u00e6de 43, 3. th, 1112 K\u00f8benhavn K",
                "value": "0ead9b4d-c615-442d-8447-b328a73b5b39",
                "value2": None,
            },
            "2ef51a73-ad7d-4ee7-e044-0003ba298018": {
                "href": "https://www.openstreetmap.org/"
                "?mlon=12.3647784&mlat=55.73404048&zoom=16",
                "name": "Hold-An Vej 7, 1., 2750 Ballerup",
                "value": "2ef51a73-ad7d-4ee7-e044-0003ba298018",
                "value2": None,
            },
            "bd7e5317-4a9e-437b-8923-11156406b117": {
                "href": None,
                "name": "Hold-An Vej 7, 2750 Ballerup",
                "value": "bd7e5317-4a9e-437b-8923-11156406b117",
                "value2": None,
            },
        }
        for addrid, expected in sorted(addresses.items()):
            with self.subTest(addrid):
                with dar_loader():
                    actual = await address.get_one_address(
                        {
                            "relationer": {
                                "adresser": [
                                    {
                                        "objekttype": "DAR",
                                        "urn": "urn:dar:{}".format(addrid),
                                    }
                                ]
                            }
                        },
                    )
                self.assertEqual(actual, expected)

    async def test_bad_scope(self):
        with self.assertRaisesRegex(
            exceptions.HTTPException, "Invalid address scope type"
        ):
            await address.get_one_address(
                {
                    "relationer": {
                        "adresser": [
                            {
                                "objekttype": "kaflaflibob",
                                "uuid": "00000000-0000-0000-0000-000000000000",
                            }
                        ]
                    }
                },
            )


class TestAddressLookup(tests.cases.TestCase):
    @freezegun.freeze_time("2016-06-06")
    @util.MockAioresponses(passthrough=["http://localhost"])
    def test_autocomplete_no_municipality(self, mock):
        url = URL("http://mox/organisation/organisation")
        mock.get(
            url,
            payload={
                "results": [
                    [
                        {
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
                            ],
                        }
                    ]
                ]
            },
        )

        self.assertRequestResponse(
            "/service/o/00000000-0000-0000-0000-000000000000/"
            "address_autocomplete/?q=42",
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )

        call_args = one(mock.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2016-06-06T00:00:00+02:00",
                "virkningtil": "2016-06-06T00:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

    @freezegun.freeze_time("2016-06-06")
    @util.MockAioresponses(passthrough=["http://localhost"])
    def test_autocomplete_invalid_municipality(self, mock):
        url = URL("http://mox/organisation/organisation")
        mock.get(
            url,
            payload={
                "results": [
                    [
                        {
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
                            ],
                        }
                    ]
                ]
            },
        )

        self.assertRequestResponse(
            "/service/o/00000000-0000-0000-0000-000000000000/"
            "address_autocomplete/?q=42",
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )

        call_args = one(mock.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2016-06-06T00:00:00+02:00",
                "virkningtil": "2016-06-06T00:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

    @freezegun.freeze_time("2016-06-06")
    @util.MockAioresponses(passthrough=["http://localhost"])
    def test_autocomplete_missing_org(self, mock):
        url = URL("http://mox/organisation/organisation")
        mock.get(
            url,
            payload={"results": []},
        )

        self.assertRequestResponse(
            "/service/o/00000000-0000-0000-0000-000000000000/"
            "address_autocomplete/?q=42",
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )

        call_args = one(mock.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2016-06-06T00:00:00+02:00",
                "virkningtil": "2016-06-06T00:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

    @freezegun.freeze_time("2017-07-28")
    @util.MockAioresponses(("dawa-autocomplete.json",))
    def test_autocomplete_global(self, mock):
        found = [
            {
                "location": {
                    "name": "Strandlodsvej 25M, 2300 K\u00f8benhavn S",
                    "uuid": "18fbd56e-c6b2-4d0f-bb08-80133edb896e",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 1. th, 2300 K\u00f8benhavn S",
                    "uuid": "b18f681b-dcce-4a1f-9231-08182653dbd9",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 1. tv, 2300 K\u00f8benhavn S",
                    "uuid": "21483493-bf6d-4cdd-badd-74bc5109c7b1",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 2. th, 2300 K\u00f8benhavn S",
                    "uuid": "22bf4e3e-14f3-4096-b479-2e8d4ac090fb",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 2. tv, 2300 K\u00f8benhavn S",
                    "uuid": "d4764afd-f5f1-4038-9298-9148bcb56421",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 3. th, 2300 K\u00f8benhavn S",
                    "uuid": "13deac37-805b-4024-a6dc-4b5f6808571c",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 3. tv, 2300 K\u00f8benhavn S",
                    "uuid": "2bd96c7d-e9b5-449b-889c-f09a4c1fae50",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 4. th, 2300 K\u00f8benhavn S",
                    "uuid": "c5871526-6f4f-425c-bd3f-05b837df24cb",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 4. tv, 2300 K\u00f8benhavn S",
                    "uuid": "6ee8b42e-bfc2-42d3-974f-47791c99b375",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 5. th, 2300 K\u00f8benhavn S",
                    "uuid": "fd3fceb2-860a-4c15-b57f-795cbfda5882",
                }
            },
            {
                "location": {
                    "name": "Strandlodsvej 25M, 5. tv, 2300 K\u00f8benhavn S",
                    "uuid": "8aa7e68d-e451-43c7-9c02-705ea7a9bb40",
                }
            },
        ]

        self.assertRequestResponse(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M&global=1",
            found,
        )

        self.assertRequestResponse(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M&global=true",
            found,
        )

    @freezegun.freeze_time("2017-07-28")
    @util.MockAioresponses()
    def test_autocomplete_local(self, mock):
        url = URL("http://mox/organisation/organisation")

        def callback(url, json, **kwargs):
            if json.get("uuid") == ["456362c4-0ee4-4e5e-a72c-751239745e62"]:
                # noqa
                payload = {
                    "results": [
                        [
                            {
                                "id": "456362c4-0ee4-4e5e-a72c-751239745e62",
                                "registreringer": [
                                    {
                                        "attributter": {
                                            "organisationegenskaber": [
                                                {
                                                    "brugervendtnoegle": "AU",
                                                    "organisationsnavn": "Aarhus Universitet",  # noqa: E501
                                                    "virkning": {
                                                        "from": "2016-01-01 00:00:00+01",  # noqa: E501
                                                        "from_included": True,
                                                        "to": "infinity",
                                                        "to_included": False,
                                                    },
                                                }
                                            ]
                                        },
                                        "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",  # noqa: E501
                                        "fratidspunkt": {
                                            "graenseindikator": True,
                                            "tidsstempeldatotid": "2017-08-17T10:27:27.65144+02:00",  # noqa: E501
                                        },
                                        "livscykluskode": "Importeret",
                                        "note": "Automatisk indlæsning",
                                        "relationer": {
                                            "myndighed": [
                                                {
                                                    "urn": "urn:dk:kommune:751",
                                                    "virkning": {
                                                        "from": "2016-01-01 00:00:00+01",  # noqa: E501
                                                        "from_included": True,
                                                        "to": "infinity",
                                                        "to_included": False,
                                                    },
                                                }
                                            ]
                                        },
                                        "tilstande": {
                                            "organisationgyldighed": [
                                                {
                                                    "gyldighed": "Aktiv",
                                                    "virkning": {
                                                        "from": "2016-01-01 00:00:00+01",  # noqa: E501
                                                        "from_included": True,
                                                        "to": "infinity",
                                                        "to_included": False,
                                                    },
                                                }
                                            ]
                                        },
                                        "tiltidspunkt": {
                                            "tidsstempeldatotid": "infinity"
                                        },
                                    }
                                ],
                            }
                        ]
                    ]
                }
            else:
                payload = {
                    "results": [
                        ["456362c4-0ee4-4e5e-a72c-751239745e62"],
                    ],
                }
            return CallbackResult(payload=payload)

        mock.get(
            url,
            callback=callback,
        )

        self.assertRequestResponse(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M",
            [],
        )
