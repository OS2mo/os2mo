# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import copy
from functools import partial
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora
from mora import mapping
from more_itertools import one

from tests.cases import assert_registrations_equal
from tests.util import set_settings_contextmanager

_substitute_association = {"name": "i18n:substitute_association"}  # const
_substitute_uuid = "7626ad64-327d-481f-8b32-36c78eb12f8c"
_unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
_userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
_it_system_uuid = "0872fb72-926d-4c5c-a063-ff800b8ee697"
_it_user_uuid = "11111111-1111-1111-1111-111111111111"
_job_function_uuid = str(uuid4())


def _lora_virkning(**kwargs) -> dict[str, dict[str, bool | str]]:
    virkning = {
        "virkning": {
            "from": "2017-12-01 00:00:00+01",
            "from_included": True,
            "to": "2017-12-02 00:00:00+01",
            "to_included": False,
        },
    }
    virkning.update(kwargs)
    return virkning


def _lora_organisationfunktion(**kwargs) -> dict[str, dict[str, list[dict[str, dict[str, bool | str]]]] | str]:
    doc = {
        "livscykluskode": "Importeret",
        "tilstande": {
            "organisationfunktiongyldighed": [
                _lora_virkning(gyldighed="Aktiv"),
            ]
        },
        "note": "Oprettet i MO",
        "relationer": {
            "tilknyttedeorganisationer": [
                _lora_virkning(uuid="456362c4-0ee4-4e5e-a72c-751239745e62"),
            ],
            "tilknyttedebrugere": [
                _lora_virkning(uuid=_userid),
            ],
            "organisatoriskfunktionstype": [
                _lora_virkning(uuid="62ec821f-4179-4758-bfdf-134529d186e9"),
            ],
            "tilknyttedeenheder": [
                _lora_virkning(uuid=_unitid),
            ],
            "primær": [
                _lora_virkning(uuid="f49c797b-d3e8-4dc2-a7a8-c84265432474"),
            ],
        },
        "attributter": {
            "organisationfunktionegenskaber": [
                _lora_virkning(brugervendtnoegle="1234", funktionsnavn="Tilknytning"),
            ]
        },
    }

    for key, val in kwargs.items():
        if key in doc:
            doc[key].update(val)

    return doc


def _mo_create_it_user_doc() -> dict[str, dict[str, str | None] | dict[str, str] | str | None]:
    return {
        "type": "it",
        "uuid": _it_user_uuid,
        "itsystem": {"uuid": _it_system_uuid},
        "user_key": "usernameInItSystem",
        "person": {"uuid": _userid},
        "org_unit": {"uuid": _unitid},
        "engagement": None,
        "validity": {"from": "2017-01-01", "to": None},
    }


def _mo_return_it_user_doc() -> dict[str, dict[str, str | None] | dict[str, str] | str | None]:
    doc = _mo_create_it_user_doc()
    del doc["type"]
    doc["primary"] = None
    return doc


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "mo_data, mo_expected, lora_expected",
    [
        # 1. Test usage of "substitute" property on associations
        (
            # MO payload: extra data
            {
                "substitute": {"uuid": _substitute_uuid},
            },
            # MO response: expected extra data
            {
                "substitute": {"uuid": _substitute_uuid},
                "it": None,
                "job_function": None,
            },
            # LoRa response: expected extra data
            {
                "relationer": {
                    "tilknyttedefunktioner": [_lora_virkning(uuid=_substitute_uuid)]
                }
            },
        ),
        # 2. Test usage of "it" and "job_function" properties on associations
        (
            # MO payload: extra data
            {
                "it": {"uuid": _it_user_uuid},
                "job_function": {"uuid": _job_function_uuid},
            },
            # MO response: expected extra data
            {
                "substitute": None,
                "it": [_mo_return_it_user_doc()],
                "job_function": {"uuid": _job_function_uuid},
            },
            # LoRa response: expected extra data
            {
                "relationer": {
                    "tilknyttedeitsystemer": [_lora_virkning(uuid=_it_user_uuid)],
                    "tilknyttedefunktioner": [_lora_virkning(uuid=_job_function_uuid)],
                }
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_association(
    service_client: TestClient,
    mo_data: dict[str, Any],
    mo_expected: dict[str, Any],
    lora_expected: dict[str, Any],
) -> None:
    def url(employee_uuid: str, **kwargs) -> str:
        base = f"/service/e/{employee_uuid}/details/association"
        args = {"validity": "future", "only_primary_uuid": "1"}
        if "it" in mo_data and "first_party_perspective" not in kwargs:
            args.update(it="1")
        if kwargs:
            args.update(**kwargs)
        return f"{base}?{urlencode(args)}"

    seed_substitute_roles = partial(
        set_settings_contextmanager,
        confdb_substitute_roles='["62ec821f-4179-4758-bfdf-134529d186e9"]',
    )

    # Create an "IT User" (aka. "IT system binding")
    response = service_client.request(
        "POST", "/service/details/create", json=_mo_create_it_user_doc()
    )
    assert response.status_code == 201

    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    association_uuid = "00000000-0000-0000-0000-000000000000"

    payload = [
        {
            "type": "association",
            "uuid": association_uuid,
            "org_unit": {"uuid": _unitid},
            "person": {"uuid": _userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "user_key": "1234",
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
        }
    ]

    payload[0].update(mo_data)

    with seed_substitute_roles():
        response = service_client.request(
            "POST", "/service/details/create", json=payload
        )
        assert response.status_code == 201
        assert response.json() == [association_uuid]

    # Check that we created the expected "organisationfunktion" in LoRa
    expected = _lora_organisationfunktion(**lora_expected)
    associations = await c.organisationfunktion.fetch(
        tilknyttedebrugere=_userid, funktionsnavn="Tilknytning"
    )
    associationid = one(associations)
    actual_association = await c.organisationfunktion.get(associationid)
    assert_registrations_equal(expected, actual_association)

    # Check that we get the expected response from MO, case 1
    expected = {
        "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "dynamic_classes": [],
        "org_unit": {"uuid": _unitid},
        "person": {"uuid": _userid},
        "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
        "user_key": "1234",
        "uuid": "00000000-0000-0000-0000-000000000000",
        "validity": {"from": "2017-12-01", "to": "2017-12-01"},
    }
    expected.update(mo_expected)
    with seed_substitute_roles():
        response = service_client.request("GET", url(_userid))
        assert response.status_code == 200
        assert response.json() == [expected]

    # Check that we get the expected response from MO, case 2
    expected = {
        "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "dynamic_classes": [],
        "org_unit": {"uuid": _unitid},
        "person": {"uuid": _userid},
        "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
        "user_key": "1234",
        "uuid": "00000000-0000-0000-0000-000000000000",
        "validity": {"from": "2017-12-01", "to": "2017-12-01"},
        "first_party_association_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "third_party_associated": {"uuid": _substitute_uuid},
        "third_party_association_type": _substitute_association,
    }
    expected.update(mo_expected)
    with seed_substitute_roles():
        response = service_client.request(
            "GET",
            url(_userid, first_party_perspective="1"),
        )
        assert response.status_code == 200
        assert response.json() == ([expected] if "it" not in mo_data else [])

    # Check that we get the expected response from MO, case 3
    response = service_client.request("GET", url(_substitute_uuid))
    assert response.status_code == 200
    assert response.json() == []

    # Check that we get the expected response from MO, case 2
    expected = {
        "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "dynamic_classes": [],
        "org_unit": {"uuid": _unitid},
        "person": {"uuid": _userid},
        "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
        "user_key": "1234",
        "uuid": "00000000-0000-0000-0000-000000000000",
        "validity": {"from": "2017-12-01", "to": "2017-12-01"},
        "first_party_association_type": _substitute_association,
        "third_party_associated": {"uuid": _userid},
        "third_party_association_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
    }
    expected.update(mo_expected)
    with seed_substitute_roles():
        response = service_client.request(
            "GET", url(_substitute_uuid, first_party_perspective="1")
        )
        assert response.status_code == 200
        assert response.json() == ([expected] if "it" not in mo_data else [])


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_vacant_association(service_client: TestClient) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    # test multiple valid formats
    association_uuid = "00000000-0000-0000-0000-000000000000"
    association_uuid2 = "00000000-0000-0000-0000-000000000001"

    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

    def payload(assoc_uuid: str, include_person=True):
        """
        :param assoc_uuid: uuid to use
        :param include_person: change between formats (both legal)
        :return: valid assoication payload
        """

        main = {
            "type": "association",
            "uuid": assoc_uuid,
            "org_unit": {"uuid": unitid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "substitute": {"uuid": subid},
            "user_key": "1234",
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
            "it": None,
            "job_function": None,
        }
        if include_person:
            main["person"] = None
        return [main]

    with set_settings_contextmanager(
        confdb_substitute_roles='["62ec821f-4179-4758-bfdf-134529d186e9"]'
    ):
        response = service_client.request(
            "POST", "/service/details/create", json=payload(association_uuid)
        )
        assert response.status_code == 201
        assert response.json() == [association_uuid]

        response = service_client.request(
            "POST",
            "/service/details/create",
            json=payload(association_uuid2, include_person=False),
        )
        assert response.status_code == 201
        assert response.json() == [association_uuid2]

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
            "tilknyttedefunktioner": [
                {
                    "uuid": subid,
                    "virkning": {
                        "from": "2017-12-01 00:00:00+01",
                        "from_included": True,
                        "to": "2017-12-02 00:00:00+01",
                        "to_included": False,
                    },
                }
            ],
            "primær": [
                {
                    "uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474",
                    "virkning": {
                        "from": "2017-12-01 00:00:00+01",
                        "from_included": True,
                        "to": "2017-12-02 00:00:00+01",
                        "to_included": False,
                    },
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
                    "funktionsnavn": "Tilknytning",
                }
            ]
        },
    }

    associations = await c.organisationfunktion.fetch(
        tilknyttedeenheder=unitid,
        tilknyttedeorganisationer="456362c4-0ee4-4e5e-a72c-751239745e62",
        brugervendtnoegle="1234",
        funktionsnavn="Tilknytning",
    )
    assert len(associations) == 2
    for associationid in associations:
        # assert we got back one of the newly created associations (ie. exists)
        assert associationid in (association_uuid, association_uuid2)

        # check that the content is also as expected
        actual_association = await c.organisationfunktion.get(associationid)

        assert_registrations_equal(expected, actual_association)

    def assoc_content_only_primary_uuid(assoc_uuid: str):
        """
        creates expected format

        :param assoc_uuid:
        :return:
        """
        return {
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [],
            "org_unit": {"uuid": unitid},
            "person": None,
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "user_key": "1234",
            "uuid": assoc_uuid,
            "substitute": {"uuid": subid},
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            "it": None,
            "job_function": None,
        }

    expected = [
        assoc_content_only_primary_uuid(association_uuid),
        assoc_content_only_primary_uuid(association_uuid2),
    ]

    with set_settings_contextmanager(
        confdb_substitute_roles='["62ec821f-4179-4758-bfdf-134529d186e9"]'
    ):
        # contains sorting (ie. unordered comparison)
        response = service_client.request(
            "GET",
            f"/service/ou/{unitid}/details/association",
            params={"validity": "future", "only_primary_uuid": 1},
        )
        assert response.status_code == 200
        assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_association_with_dynamic_classes(
    service_client: TestClient,
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    association_uuid = "00000000-0000-0000-0000-000000000000"
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
    classid = "cafebabe-c370-4502-81c2-7697009c9053"

    payload = [
        {
            "type": "association",
            "uuid": association_uuid,
            "dynamic_classes": [{"uuid": classid}],
            "org_unit": {"uuid": unitid},
            "person": {"uuid": userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "user_key": "1234",
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201
    assert response.json() == [association_uuid]

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
            "tilknyttedeklasser": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-12-02 00:00:00+01",
                        "from_included": True,
                        "from": "2017-12-01 00:00:00+01",
                    },
                    "uuid": classid,
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
            "primær": [
                {
                    "uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474",
                    "virkning": {
                        "from": "2017-12-01 00:00:00+01",
                        "from_included": True,
                        "to": "2017-12-02 00:00:00+01",
                        "to_included": False,
                    },
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
                    "funktionsnavn": "Tilknytning",
                }
            ]
        },
    }

    associations = await c.organisationfunktion.fetch(
        tilknyttedebrugere=userid, funktionsnavn="Tilknytning"
    )
    associationid = one(associations)

    actual_association = await c.organisationfunktion.get(associationid)

    assert_registrations_equal(expected, actual_association)

    expected = [
        {
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "dynamic_classes": [{"uuid": "cafebabe-c370-4502-81c2-7697009c9053"}],
            "org_unit": {"uuid": unitid},
            "person": {"uuid": userid},
            "primary": {"uuid": "f49c797b-d3e8-4dc2-a7a8-c84265432474"},
            "user_key": "1234",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "substitute": None,
            "validity": {"from": "2017-12-01", "to": "2017-12-01"},
            "it": None,
            "job_function": None,
        }
    ]
    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/association",
        params={"validity": "future", "only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_association_with_preexisting(service_client: TestClient) -> None:
    """More than one active association is allowed for each employee in each
    org unit"""

    # Check the POST request
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    payload = {
        "type": "association",
        "org_unit": {"uuid": unitid},
        "person": {"uuid": userid},
        "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "dynamic_classes": [],
        "validity": {
            "from": "2017-12-01",
            "to": "2017-12-01",
        },
    }
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    associations = await c.organisationfunktion.fetch(
        tilknyttedeenheder=unitid,
        tilknyttedebrugere=userid,
        funktionsnavn=mapping.ASSOCIATION_KEY,
    )
    assert len(associations) == 1

    # validation
    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
                "org_unit": {"uuid": unitid},
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "validity": {
                    "from": "2017-12-02",
                    "to": "2017-12-02",
                },
                "org_unit": {"uuid": unitid},
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_association_move(service_client: TestClient) -> None:
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    unitid = "b688513d-11f7-4efc-b679-ab082a2055d0"
    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "data": {
                "org_unit": {"uuid": unitid},
                "validity": {
                    "from": "2018-04-01",
                    "to": "2019-03-31",
                },
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    expected_association = {
        "note": "Rediger tilknytning",
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
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
                        "to": "2018-04-01 00:00:00+02",
                    },
                },
                {
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2019-04-01 00:00:00+02",
                        "to": "infinity",
                    },
                },
                {
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2018-04-01 00:00:00+02",
                        "to": "2019-04-01 00:00:00+02",
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
                        "to": "infinity",
                    },
                    "brugervendtnoegle": "bvn",
                    "funktionsnavn": "Tilknytning",
                }
            ]
        },
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual_association = await c.organisationfunktion.get(association_uuid)

    assert_registrations_equal(expected_association, actual_association)

    expected = [
        {
            "association_type": {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            },
            "dynamic_classes": [],
            "org_unit": {
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "primary": None,
            "user_key": "bvn",
            "substitute": None,
            "uuid": association_uuid,
            "validity": {
                "from": "2018-04-01",
                "to": "2019-03-31",
            },
            "it": None,
            "job_function": None,
        }
    ]
    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/association",
        params={"at": "2018-06-01", "only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_terminate_association_via_user(service_client: TestClient) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

    payload = {"validity": {"to": "2017-11-30"}}
    response = service_client.request(
        "POST", f"/service/e/{userid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid

    expected = {
        "note": "Afsluttet",
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
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
                    "funktionsnavn": "Tilknytning",
                }
            ]
        },
    }

    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    actual_association = await c.organisationfunktion.get(association_uuid)
    assert actual_association is not None

    # drop lora-generated timestamps & users
    del (
        actual_association["fratidspunkt"],
        actual_association["tiltidspunkt"],
        actual_association["brugerref"],
    )

    assert actual_association == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_association_from_missing_unit(service_client: TestClient) -> None:
    unitid = "00000000-0000-0000-0000-000000000000"
    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

    payload = [
        {
            "type": "association",
            "org_unit": {"uuid": unitid},
            "person": {"uuid": userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "address": {
                "address_type": {
                    "example": "20304060",
                    "name": "Telefonnummer",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                },
                "value": "33369696",
            },
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 404
    assert response.json() == {
        "description": "Org unit not found.",
        "error": True,
        "error_key": "E_ORG_UNIT_NOT_FOUND",
        "org_unit_uuid": "00000000-0000-0000-0000-000000000000",
        "status": 404,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_association_succeeds_on_two_associations(
    service_client: TestClient,
) -> None:
    """An employee can have more than one active association per org unit"""

    # These are the user/unit ids on the already existing association
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

    payload = [
        {
            "type": "association",
            "org_unit": {"uuid": unitid},
            "person": {"uuid": userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "address": {"uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80"},
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_association_with_preexisting(service_client: TestClient) -> None:
    """An employee cannot have more than one active association per org
    unit"""
    # These are the user/unit ids on the already existing association
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json=[
            {
                "type": "association",
                "uuid": association_uuid,
                "validity": {"to": "2017-02-01"},
            }
        ],
    )
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    response = service_client.request(
        "POST",
        "/service/details/create",
        json=[
            {
                "type": "association",
                "org_unit": {"uuid": unitid},
                "person": {"uuid": userid},
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "address": {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefonnummer",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                    "value": "33369696",
                },
                "validity": {
                    "from": "2018-01-01",
                    "to": None,
                },
            }
        ],
    )
    assert response.status_code == 201


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_association_no_unit(service_client: TestClient) -> None:
    # Check the POST request
    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

    payload = [
        {
            "type": "association",
            "person": {"uuid": userid},
            "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "address": {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                },
                "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
            },
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing org_unit",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "org_unit",
        "obj": payload[0],
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_association_fails_on_empty_payload(service_client: TestClient) -> None:
    payload = [
        {
            "type": "association",
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing org_unit",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "org_unit",
        "obj": {"type": "association"},
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@set_settings_contextmanager(
    confdb_substitute_roles='["bcd05828-cc10-48b1-bc48-2f0d204859b2"]'
)
def test_edit_association(service_client: TestClient) -> None:
    # Check the POST request
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
    subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "dynamic_classes": [],
            "data": {
                "association_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "substitute": {
                    "uuid": subid,
                },
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    response = service_client.request(
        "GET",
        f"/service/ou/{unitid}/details/association",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "association_type": {
                "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
            },
            "dynamic_classes": [],
            "org_unit": {
                "uuid": unitid,
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "primary": None,
            "user_key": "bvn",
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "substitute": {
                "uuid": subid,
            },
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
            "it": None,
            "job_function": None,
        }
    ]

    # Change to vacant
    new_req = copy.deepcopy(req)
    new_req[0]["data"]["person"] = None

    response = service_client.request("POST", "/service/details/edit", json=new_req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    response = service_client.request(
        "GET",
        f"/service/ou/{unitid}/details/association",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "association_type": {
                "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
            },
            "dynamic_classes": [],
            "org_unit": {
                "uuid": unitid,
            },
            "person": None,
            "primary": None,
            "user_key": "bvn",
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "substitute": {
                "uuid": subid,
            },
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
            "it": None,
            "job_function": None,
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@set_settings_contextmanager(
    confdb_substitute_roles='["bcd05828-cc10-48b1-bc48-2f0d204859b2"]'
)
def test_edit_association_substitute(service_client: TestClient) -> None:
    """Test that substitute field is removed when writing an association
    type that is not meant to have substitutes"""
    # Check the POST request
    unitid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
    subid = "7626ad64-327d-481f-8b32-36c78eb12f8c"

    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "dynamic_classes": [],
            "data": {
                "association_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "substitute": {"uuid": subid},
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    req = [
        {
            "type": "association",
            "uuid": association_uuid,
            "dynamic_classes": [],
            "data": {
                "association_type": {"uuid": "46de8c9f-ecbe-4638-8b2b-386845729c9a"},
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [association_uuid]

    response = service_client.request(
        "GET",
        f"/service/ou/{unitid}/details/association",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "association_type": {
                "uuid": "46de8c9f-ecbe-4638-8b2b-386845729c9a",
            },
            "dynamic_classes": [],
            "org_unit": {
                "uuid": unitid,
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "primary": None,
            "user_key": "bvn",
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "substitute": None,
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
            "it": None,
            "job_function": None,
        }
    ]

    response = service_client.request(
        "GET",
        f"/service/ou/{subid}/details/association",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_terminate_association_directly(service_client: TestClient) -> None:
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    associationid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    payload = {
        "type": "association",
        "uuid": associationid,
        "validity": {"to": "2017-11-30"},
    }

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/association",
        params={"validity": "present"},
    )
    assert response.status_code == 200
    orig = response.json()

    expected = copy.deepcopy(orig)
    expected[0]["validity"]["to"] = "2017-11-30"

    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == associationid

    response = service_client.request(
        "GET", f"/service/e/{userid}/details/association", params={"validity": "past"}
    )
    assert response.status_code == 200
    assert response.json() == []

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/association",
        params={"validity": "present"},
    )
    assert response.status_code == 200
    assert response.json() == expected

    response = service_client.request(
        "GET", f"/service/e/{userid}/details/association", params={"validity": "future"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_terminate_association_in_the_past(service_client: TestClient) -> None:
    associationid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"

    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json={
            "type": "association",
            "uuid": associationid,
            "validity": {"to": "2017-11-30"},
        },
    )
    assert response.status_code == 200
    assert response.json() == associationid
