# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json

import freezegun
import pytest
import respx
from httpx import Response

import tests.cases
from tests import util


@pytest.mark.usefixtures("mock_asgi_transport")
class AsyncTestAddressLookup(tests.cases.AsyncTestCase):
    @freezegun.freeze_time("2016-06-06")
    @respx.mock
    async def test_autocomplete_no_municipality(self):
        route = respx.get("http://localhost/lora/organisation/organisation").mock(
            return_value=Response(
                200,
                json={
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
        )

        mo_url = (
            "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
        )
        respx.get(mo_url).pass_through()

        await self.assertRequestResponse(
            mo_url,
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )
        assert len(route.calls) == 2

        assert json.loads(route.calls[0].request.read()) == {
            "bvn": "%",
            "virkningfra": "-infinity",
            "list": "True",
            "virkningtil": "infinity",
            "konsolider": "True",
        }
        assert json.loads(route.calls[1].request.read()) == {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "virkningfra": "2016-06-06T00:00:00+00:00",
            "virkningtil": "2016-06-06T00:00:00.001000+00:00",
            "konsolider": "True",
        }

    @freezegun.freeze_time("2016-06-06")
    @respx.mock
    async def test_autocomplete_invalid_municipality(self):
        route = respx.get("http://localhost/lora/organisation/organisation").mock(
            return_value=Response(
                200,
                json={
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
        )
        mo_url = (
            "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
        )
        respx.get(mo_url).pass_through()

        await self.assertRequestResponse(
            mo_url,
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )
        assert len(route.calls) == 2

        assert json.loads(route.calls[0].request.read()) == {
            "bvn": "%",
            "virkningfra": "-infinity",
            "list": "True",
            "virkningtil": "infinity",
            "konsolider": "True",
        }
        assert json.loads(route.calls[1].request.read()) == {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "virkningfra": "2016-06-06T00:00:00+00:00",
            "virkningtil": "2016-06-06T00:00:00.001000+00:00",
            "konsolider": "True",
        }

    @freezegun.freeze_time("2016-06-06")
    @respx.mock
    async def test_autocomplete_missing_org(self):
        route = respx.get("http://localhost/lora/organisation/organisation").mock(
            return_value=Response(200, json={"results": []})
        )
        mo_url = (
            "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
        )
        respx.get(mo_url).pass_through()

        await self.assertRequestResponse(
            mo_url,
            {
                "error": True,
                "error_key": "E_NO_LOCAL_MUNICIPALITY",
                "description": "No local municipality found.",
                "status": 400,
            },
            status_code=400,
        )
        assert len(route.calls) == 1
        assert json.loads(route.calls[0].request.read()) == {
            "bvn": "%",
            "virkningfra": "-infinity",
            "list": "True",
            "virkningtil": "infinity",
            "konsolider": "True",
        }

    @freezegun.freeze_time("2017-07-28")
    @util.MockAioresponses(("dawa-autocomplete.json",))
    async def test_autocomplete_global(self, mock):
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
        mo_url1 = (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M&global=1"
        )
        mo_url2 = (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M&global=true"
        )
        respx.get(mo_url1).pass_through()
        respx.get(mo_url2).pass_through()

        await self.assertRequestResponse(mo_url1, found)
        await self.assertRequestResponse(mo_url2, found)

    @freezegun.freeze_time("2017-07-28")
    @respx.mock
    @pytest.mark.xfail
    async def test_autocomplete_local(self):
        url = "http://localhost/lora/organisation/organisation"
        respx.get(url).mock(
            return_value=Response(
                200,
                json={
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
                },
            )
        )

        respx.get(
            "https://api.dataforsyningen.dk/adgangsadresser/autocomplete"
            "?per_side=5&noformat=1&q=Strandlodsvej+25M&kommunekode=751"
        ).pass_through()
        respx.get(
            "https://api.dataforsyningen.dk/adresser/autocomplete"
            "?per_side=10&noformat=1&q=Strandlodsvej+25M&kommunekode=751"
        ).pass_through()
        mo_url = (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
            "address_autocomplete/?q=Strandlodsvej+25M"
        )
        respx.get(mo_url).pass_through()

        await self.assertRequestResponse(mo_url, [])
