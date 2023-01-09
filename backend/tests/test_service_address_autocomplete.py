# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import urllib.parse

import pytest

from tests import util

get_addrs_mock_resp = [
    {
        "adresse": {
            "d\u00f8r": "th",
            "etage": "1",
            "href": "https://dawa.aws.dk/adresser/b18f681b-dcce-4a1f-9231-08182653dbd9",
            "husnr": "25M",
            "id": "b18f681b-dcce-4a1f-9231-08182653dbd9",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 1. th, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "tv",
            "etage": "1",
            "href": "https://dawa.aws.dk/adresser/21483493-bf6d-4cdd-badd-74bc5109c7b1",
            "husnr": "25M",
            "id": "21483493-bf6d-4cdd-badd-74bc5109c7b1",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 1. tv, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "th",
            "etage": "2",
            "href": "https://dawa.aws.dk/adresser/22bf4e3e-14f3-4096-b479-2e8d4ac090fb",
            "husnr": "25M",
            "id": "22bf4e3e-14f3-4096-b479-2e8d4ac090fb",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 2. th, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "tv",
            "etage": "2",
            "href": "https://dawa.aws.dk/adresser/d4764afd-f5f1-4038-9298-9148bcb56421",
            "husnr": "25M",
            "id": "d4764afd-f5f1-4038-9298-9148bcb56421",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 2. tv, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "th",
            "etage": "3",
            "href": "https://dawa.aws.dk/adresser/13deac37-805b-4024-a6dc-4b5f6808571c",
            "husnr": "25M",
            "id": "13deac37-805b-4024-a6dc-4b5f6808571c",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 3. th, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "tv",
            "etage": "3",
            "href": "https://dawa.aws.dk/adresser/2bd96c7d-e9b5-449b-889c-f09a4c1fae50",
            "husnr": "25M",
            "id": "2bd96c7d-e9b5-449b-889c-f09a4c1fae50",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 3. tv, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "th",
            "etage": "4",
            "href": "https://dawa.aws.dk/adresser/c5871526-6f4f-425c-bd3f-05b837df24cb",
            "husnr": "25M",
            "id": "c5871526-6f4f-425c-bd3f-05b837df24cb",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 4. th, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "tv",
            "etage": "4",
            "href": "https://dawa.aws.dk/adresser/6ee8b42e-bfc2-42d3-974f-47791c99b375",
            "husnr": "25M",
            "id": "6ee8b42e-bfc2-42d3-974f-47791c99b375",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 4. tv, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "th",
            "etage": "5",
            "href": "https://dawa.aws.dk/adresser/fd3fceb2-860a-4c15-b57f-795cbfda5882",
            "husnr": "25M",
            "id": "fd3fceb2-860a-4c15-b57f-795cbfda5882",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 5. th, 2300 K\u00f8benhavn S",
    },
    {
        "adresse": {
            "d\u00f8r": "tv",
            "etage": "5",
            "href": "https://dawa.aws.dk/adresser/8aa7e68d-e451-43c7-9c02-705ea7a9bb40",
            "husnr": "25M",
            "id": "8aa7e68d-e451-43c7-9c02-705ea7a9bb40",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 5. tv, 2300 K\u00f8benhavn S",
    },
]


get_access_addrs_mock_resp = [
    {
        "adgangsadresse": {
            "href": "https://dawa.aws.dk/adgangsadresser/18fbd56e-c6b2-4d0f-bb08-80133edb896e",
            "husnr": "25M",
            "id": "18fbd56e-c6b2-4d0f-bb08-80133edb896e",
            "postnr": "2300",
            "postnrnavn": "K\u00f8benhavn S",
            "stormodtagerpostnr": None,
            "stormodtagerpostnrnavn": None,
            "supplerendebynavn": None,
            "vejnavn": "Strandlodsvej",
        },
        "tekst": "Strandlodsvej 25M, 2300 K\u00f8benhavn S",
    }
]


@pytest.mark.parametrize(
    "feature_flag_value,expected_result",
    [
        (
            "False",
            [
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
            ],
        ),
        (
            "True",
            [
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
            ],
        ),
    ],
)
async def test_autocomplete_access_addr_feature_flag(
    serviceapi_post, respx_mock, feature_flag_value, expected_result
):
    search_text = "Strandlodsvej 25M"
    search_text_parsed = urllib.parse.quote(search_text)

    # OBS: "global=1" is used in order to avoid "ErrorCodes.E_NO_LOCAL_MUNICIPALITY" errors
    # when using an unknown organisation (might exist, but we dont init the test DB)
    mo_url1 = (
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
        f"address_autocomplete/?q={search_text_parsed}&global=1"
    )

    respx_mock.get(
        "https://api.dataforsyningen.dk/adresser/autocomplete?"
        f"noformat=1&q={search_text_parsed}&per_side=10"
    ).respond(json=get_addrs_mock_resp)

    respx_mock.get(
        "https://api.dataforsyningen.dk/adgangsadresser/autocomplete?"
        f"noformat=1&q={search_text_parsed}&per_side=5"
    ).respond(json=get_access_addrs_mock_resp)

    with util.set_settings_contextmanager(
        dar_address_autocomplete_includes_access_addresses=feature_flag_value
    ):
        response = serviceapi_post(url=mo_url1)
        assert response.errors is None
        assert response.status_code == 200
        assert response.data == expected_result
