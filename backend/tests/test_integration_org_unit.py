# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy
from itertools import cycle
from typing import Any

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora
from mora.service import orgunit as service_orgunit
from more_itertools import one

from tests.cases import assert_registrations_equal
from tests.util import set_get_configuration

from . import util

org_unit_hierarchy_facet = {
    "description": "",
    "user_key": "org_unit_hierarchy",
    "uuid": "403eb28f-e21e-bdd6-3612-33771b098a12",
}
org_unit_type_facet = {
    "description": "",
    "user_key": "org_unit_type",
    "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
}
org_unit_level_facet = {
    "description": "",
    "user_key": "org_unit_level",
    "uuid": "77c39616-dd98-4cf5-87fb-cdb9f3a0e455",
}


@pytest.fixture(autouse=True)
def patch_orgunit_uuid(monkeypatch):
    """Fixture for patching service.orgunit's uuid4 to a static value

    autouse makes the fixture run on every test in the file
    """
    mock_uuid = "f494ad89-039d-478e-91f2-a63566554bd6"
    monkeypatch.setattr(service_orgunit, "uuid4", lambda: mock_uuid)
    yield


def expected_error_response(error_key: str, **overrides):
    errors = {
        "V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES": {
            "description": "Cannot terminate unit with active children and roles.",
            "roles": "Relateret Enhed",
            "child_count": 1,
        },
        "V_TERMINATE_UNIT_WITH_ROLES": {
            "description": "Cannot terminate unit with active roles.",
            "roles": "Adresse, Engagement, Leder, Relateret Enhed, Rollebinding, Tilknytning",
        },
        "V_DATE_OUTSIDE_ORG_UNIT_RANGE": {
            "description": "Date range exceeds validity range of associated org unit.",
            "org_unit_uuid": None,
            "valid_from": None,
            "valid_to": None,
        },
    }
    return {"error_key": error_key, **dict(errors[error_key], **overrides)}


org_unit_uuid = "85715fc7-925d-401b-822d-467eb4b163b6"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload, expected",
    [
        # No owner
        (
            {
                "type": "org_unit",
                "original": {
                    "validity": {"from": "2016-01-01 00:00:00+01", "to": None},
                    "parent": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "time_planning": None,
                    "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
                    "name": "Filosofisk Institut",
                    "uuid": org_unit_uuid,
                },
                "data": {
                    "org_unit_type": {"uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a"},
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
            {
                "note": "Rediger organisationsenhed",
                "attributter": {
                    "organisationenhedegenskaber": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "fil",
                            "enhedsnavn": "Filosofisk Institut",
                        }
                    ]
                },
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "2017-01-01 00:00:00+01",
                            },
                        },
                    ]
                },
                "relationer": {
                    "tilhoerer": [
                        {
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "overordnet": [
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "enhedstype": [
                        {
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "2017-01-01 00:00:00+01",
                            },
                        },
                        {
                            "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ],
                },
                "livscykluskode": "Rettet",
            },
        ),
        # Edit
        (
            {
                "type": "org_unit",
                "data": {
                    "uuid": org_unit_uuid,
                    "org_unit_type": {"uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a"},
                    "org_unit_level": {"uuid": "d329c924-0cd1-4599-aca8-1d89cca2bff2"},
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
            {
                "note": "Rediger organisationsenhed",
                "attributter": {
                    "organisationenhedegenskaber": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "fil",
                            "enhedsnavn": "Filosofisk Institut",
                        }
                    ]
                },
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ]
                },
                "relationer": {
                    "tilhoerer": [
                        {
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "overordnet": [
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "niveau": [
                        {
                            "uuid": "d329c924-0cd1-4599-aca8-1d89cca2bff2",
                            "virkning": {
                                "from": "2017-01-01 00:00:00+01",
                                "from_included": True,
                                "to": "infinity",
                                "to_included": False,
                            },
                        }
                    ],
                    "enhedstype": [
                        {
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "2017-01-01 00:00:00+01",
                            },
                        },
                        {
                            "uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ],
                },
                "livscykluskode": "Rettet",
            },
        ),
        # Rename
        (
            {
                "type": "org_unit",
                "data": {
                    "name": "Filosofisk Institut II",
                    "user_key": "højrespidseskilning",
                    "uuid": org_unit_uuid,
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
            {
                "note": "Rediger organisationsenhed",
                "attributter": {
                    "organisationenhedegenskaber": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "2018-01-01 00:00:00+01",
                            },
                            "brugervendtnoegle": "fil",
                            "enhedsnavn": "Filosofisk Institut",
                        },
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "højrespidseskilning",
                            "enhedsnavn": "Filosofisk Institut II",
                        },
                    ]
                },
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ]
                },
                "relationer": {
                    "tilhoerer": [
                        {
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "overordnet": [
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                    "enhedstype": [
                        {
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2016-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        }
                    ],
                },
                "livscykluskode": "Rettet",
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_org_unit(
    service_client: TestClient,
    payload: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == 200
    org_unit_uuid = response.json()

    actual = await c.organisationenhed.get(org_unit_uuid)
    assert actual is not None
    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_edit_org_unit_earlier_start_on_created(
    service_client: TestClient,
) -> None:
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {
        "type": "org_unit",
        "name": "Fake Corp",
        "parent": {"uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
        "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
        "addresses": [
            {
                "address_type": {
                    "example": "20304060",
                    "name": "Telefon",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                },
                "value": "11 22 33 44",
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                },
                "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
            },
        ],
        "validity": {
            "from": "2017-01-01",
            "to": "2017-12-31",
        },
    }

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201
    org_unit_uuid = response.json()

    req = {
        "type": "org_unit",
        "data": {
            "uuid": org_unit_uuid,
            "user_key": org_unit_uuid,
            "validity": {
                "from": "2016-06-01",
            },
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200

    expected = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": org_unit_uuid,
                    "enhedsnavn": "Fake Corp",
                    "virkning": {
                        "from": "2016-06-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
        },
        "livscykluskode": "Rettet",
        "note": "Rediger organisationsenhed",
        "relationer": {
            "enhedstype": [
                {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                    "virkning": {
                        "from": "2016-06-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "overordnet": [
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "virkning": {
                        "from": "2016-06-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "tilhoerer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2016-06-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from": "2016-06-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
        },
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.organisationenhed.get(org_unit_uuid)

    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01")
async def test_create_org_unit(service_client: TestClient) -> None:
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {
        "name": "Fake Corp",
        "time_planning": {
            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
        },
        "parent": {"uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
        "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
        "org_unit_level": {"uuid": "0f015b67-f250-43bb-9160-043ec19fad48"},
        "org_unit_hierarchy": {"uuid": "12345678-abcd-abcd-1234-12345678abcd"},
        "details": [
            {
                "type": "address",
                "address_type": {
                    "example": "20304060",
                    "name": "Telefon",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                },
                "org": org,
                "validity": {
                    "from": "2016-02-04",
                    "to": "2017-10-21",
                },
                "value": "11223344",
            },
            {
                "type": "address",
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                },
                "org": org,
                "validity": {
                    "from": "2016-02-04",
                    "to": "2017-10-21",
                },
                "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
            },
        ],
        "validity": {
            "from": "2016-02-04",
            "to": "2017-10-21",
        },
    }

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201
    unitid = response.json()

    expected = {
        "livscykluskode": "Importeret",
        "note": "Oprettet i MO",
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "brugervendtnoegle": unitid,
                    "enhedsnavn": "Fake Corp",
                }
            ]
        },
        "relationer": {
            "opgaver": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "objekttype": "tidsregistrering",
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                }
            ],
            "overordnet": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                }
            ],
            "tilhoerer": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                }
            ],
            "enhedstype": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                }
            ],
            "niveau": [
                {
                    "uuid": "0f015b67-f250-43bb-9160-043ec19fad48",
                    "virkning": {
                        "from": "2016-02-04 00:00:00+01",
                        "from_included": True,
                        "to": "2017-10-22 00:00:00+02",
                        "to_included": False,
                    },
                }
            ],
            "opmærkning": [
                {
                    "uuid": "12345678-abcd-abcd-1234-12345678abcd",
                    "virkning": {
                        "from": "2016-02-04 00:00:00+01",
                        "from_included": True,
                        "to": "2017-10-22 00:00:00+02",
                        "to_included": False,
                    },
                }
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "2017-10-22 00:00:00+02",
                        "from_included": True,
                        "from": "2016-02-04 00:00:00+01",
                    },
                    "gyldighed": "Aktiv",
                }
            ]
        },
    }

    actual_org_unit = await c.organisationenhed.get(unitid)
    assert_registrations_equal(expected, actual_org_unit)

    org_unit_type_institute_without_published = deepcopy(org_unit_type_institute)
    org_unit_type_institute_without_published.pop("published")

    org_unit_type_department_without_published = deepcopy(org_unit_type_department)
    org_unit_type_department_without_published.pop("published")

    with set_get_configuration("mora.service.shimmed.org_unit.get_configuration"):
        response = service_client.request("GET", f"/service/ou/{unitid}/")
        assert response.status_code == 200
        assert response.json() == {
            "location": "Overordnet Enhed",
            "name": "Fake Corp",
            "org": org,
            "org_unit_level": {
                "example": None,
                "facet": org_unit_level_facet,
                "name": "Niveau 10",
                "full_name": "Niveau 10",
                "owner": None,
                "scope": None,
                "top_level_facet": org_unit_level_facet,
                "user_key": "orgunitlevel10",
                "uuid": "0f015b67-f250-43bb-9160-043ec19fad48",
            },
            "time_planning": org_unit_type_institute_without_published,
            "org_unit_type": org_unit_type_institute_without_published,
            "parent": {
                "location": "",
                "name": "Overordnet Enhed",
                "org": org,
                "org_unit_level": None,
                "org_unit_type": org_unit_type_department_without_published,
                "parent": None,
                "time_planning": None,
                "user_key": "root",
                "user_settings": {"orgunit": {}},
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {"from": "2016-01-01", "to": None},
            },
            "user_key": unitid,
            "user_settings": {"orgunit": {}},
            "uuid": unitid,
            "validity": {"from": "2016-02-04", "to": "2017-10-21"},
        }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_rename_root_org_unit(service_client: TestClient) -> None:
    # Test renaming root units

    org_unit_uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    req = {
        "type": "org_unit",
        "data": {
            "parent": None,
            "name": "Whatever",
            "uuid": org_unit_uuid,
            "validity": {
                "from": "2018-01-01T00:00:00+01",
            },
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    expected = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": "root",
                    "enhedsnavn": "Whatever",
                    "virkning": {
                        "from": "2018-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "brugervendtnoegle": "root",
                    "enhedsnavn": "Overordnet Enhed",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "2018-01-01 00:00:00+01",
                        "to_included": False,
                    },
                },
            ]
        },
        "livscykluskode": "Rettet",
        "note": "Rediger organisationsenhed",
        "relationer": {
            "enhedstype": [
                {
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilhoerer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ]
        },
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.organisationenhed.get(org_unit_uuid)

    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_rename_root_org_unit_no_parent(service_client: TestClient) -> None:
    # Test renaming root units

    org_unit_uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    req = {
        "type": "org_unit",
        "data": {
            "name": "Whatever",
            "uuid": org_unit_uuid,
            "validity": {
                "from": "2018-01-01T00:00:00+01",
            },
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    expected = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": "root",
                    "enhedsnavn": "Whatever",
                    "virkning": {
                        "from": "2018-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "brugervendtnoegle": "root",
                    "enhedsnavn": "Overordnet Enhed",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "2018-01-01 00:00:00+01",
                        "to_included": False,
                    },
                },
            ]
        },
        "livscykluskode": "Rettet",
        "note": "Rediger organisationsenhed",
        "relationer": {
            "enhedstype": [
                {
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilhoerer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ]
        },
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.organisationenhed.get(org_unit_uuid)

    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_move_org_unit(service_client: TestClient):
    "Test successfully moving organisational units"

    org_unit_uuid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    req = {
        "type": "org_unit",
        "data": {
            "parent": {"uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"},
            "uuid": org_unit_uuid,
            "validity": {
                "from": "2017-07-01",
            },
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    expected = {
        "note": "Rediger organisationsenhed",
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                    "brugervendtnoegle": "hum",
                    "enhedsnavn": "Humanistisk fakultet",
                }
            ]
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                },
            ]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "2017-07-01 00:00:00+02",
                        "to_included": False,
                    },
                },
                {
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "virkning": {
                        "from": "2017-07-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "enhedstype": [
                {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "opmærkning": [
                {
                    "uuid": "69de6410-bfe7-bea5-e6cc-376b3302189c",
                    "virkning": {
                        "from": "2016-12-31 23:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
        "livscykluskode": "Rettet",
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.organisationenhed.get(org_unit_uuid)

    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_move_org_unit_to_root(service_client: TestClient):
    "Test successfully moving organisational units"

    org_unit_uuid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    req = {
        "type": "org_unit",
        "data": {
            "parent": None,
            "uuid": org_unit_uuid,
            "validity": {
                "from": "2017-07-01",
            },
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    expected = {
        "note": "Rediger organisationsenhed",
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                    "brugervendtnoegle": "hum",
                    "enhedsnavn": "Humanistisk fakultet",
                }
            ]
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                },
            ]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "virkning": {
                        "from": "2016-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "2017-07-01 00:00:00+02",
                        "to_included": False,
                    },
                },
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from": "2017-07-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "enhedstype": [
                {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2016-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "opmærkning": [
                {
                    "uuid": "69de6410-bfe7-bea5-e6cc-376b3302189c",
                    "virkning": {
                        "from": "2016-12-31 23:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
        "livscykluskode": "Rettet",
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.organisationenhed.get(org_unit_uuid)

    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_move_org_unit_wrong_org(
    another_transaction, service_client: TestClient
) -> None:
    """Verify that we cannot move a unit into another organisation"""

    async with another_transaction():
        org_unit_uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"
        other_org_uuid = await util.load_fixture(
            "organisation/organisation",
            "create_organisation_AU.json",
        )

        c = lora.Connector()

        other_unit = util.get_fixture("create_organisationenhed_root.json")
        other_unit["relationer"]["tilhoerer"][0]["uuid"] = other_org_uuid
        other_unit["relationer"]["overordnet"][0]["uuid"] = other_org_uuid

        other_unit_uuid = await c.organisationenhed.create(other_unit)

    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "org_unit",
            "data": {
                "parent": {
                    "uuid": other_unit_uuid,
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2018-01-01",
                },
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "description": "Unit belongs to an organisation different "
        "from the current one.",
        "error": True,
        "error_key": "V_UNIT_OUTSIDE_ORG",
        "org_unit_uuid": other_unit_uuid,
        "current_org_uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        "target_org_uuid": other_org_uuid,
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_edit_parent_reads_from_previous_relation(
    service_client: TestClient,
) -> None:
    # In this test, the org unit tree looks like this:
    #
    # "Overordnet Enhed" - 456362c4-0ee4-4e5e-a72c-751239745e62
    #   -> "Humanistisk Fakultet" - 9d07123e-47ac-4a9a-88c8-da82e3a4bc9e
    #   -> other children ...
    # "Lønorganisation" - b1f69701-86d8-496e-a3f1-ccef18ac1958
    #   -> one child unit
    #
    # During the test, we alternate the parent of "Humanistisk Fakultet"
    # between "Overordnet Enhed" and "Lønorganisation", adding a year to
    # the start of the validity period each time. The expected result is
    # that the parent returned by the MO API is the parent we specified.

    overordnet_enhed = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    lønorganisation = "b1f69701-86d8-496e-a3f1-ccef18ac1958"
    humanistisk_fakultet = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    async def edit_parent(parent: str, validity: dict[str, str]):
        response = service_client.request(
            "POST",
            "/service/details/edit",
            params={"force": 1},
            json={
                "type": "org_unit",
                "data": {
                    "uuid": humanistisk_fakultet,
                    "parent": {"uuid": parent},
                    "validity": validity,
                    "name": "Not used in this test but required by the MO API",
                },
            },
        )
        assert response.status_code == 200
        assert response.json() == humanistisk_fakultet

    async def assert_parent_is(expected_parent: str, at: str):
        with freezegun.freeze_time(at):
            response = service_client.request(
                "GET", f"/service/ou/{humanistisk_fakultet}/"
            )
            assert response.status_code == 200
            doc = response.json()
            actual_parent = doc["parent"]["uuid"]
            assert actual_parent == expected_parent

    # Initial state: parent is "Overordnet Enhed"
    await assert_parent_is(overordnet_enhed, "2016-01-01")

    # Construct iterable of changes, consisting of tuples of (parent uuid,
    # validity period start). The parent uuid alternates between
    # "Lønorganisation" and "Overordnet Enhed".
    changes = zip(
        cycle((lønorganisation, overordnet_enhed)),
        (f"{year}-01-01" for year in range(2017, 2022)),
    )

    # Apply each change, and assert result is correct
    for expected_parent, validity_start in changes:
        await edit_parent(expected_parent, {"from": validity_start})
        await assert_parent_is(expected_parent, validity_start)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
async def test_terminate_not_allowed_with_addrs(service_client: TestClient) -> None:
    response = service_client.request(
        "POST",
        "/service/ou/f494ad89-039d-478e-91f2-a63566554666/terminate",
        json={"validity": {"to": "2018-09-30"}},
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "status": 400,
        "error_key": "V_TERMINATE_UNIT_WITH_ROLES",
        "description": "Cannot terminate unit with active roles.",
        "roles": "Adresse",
    }


org = {
    "name": "Aarhus Universitet",
    "user_key": "AU",
    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
}
org_unit_type_department = {
    "example": None,
    "facet": org_unit_type_facet,
    "full_name": "Afdeling",
    "name": "Afdeling",
    "owner": None,
    "published": "Publiceret",
    "scope": None,
    "top_level_facet": org_unit_type_facet,
    "user_key": "afd",
    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
}
org_unit_type_institute = {
    "example": None,
    "facet": org_unit_type_facet,
    "full_name": "Institut",
    "name": "Institut",
    "owner": None,
    "published": "Publiceret",
    "scope": None,
    "top_level_facet": org_unit_type_facet,
    "user_key": "inst",
    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
}
org_unit_type_faculty = {
    "example": None,
    "facet": org_unit_type_facet,
    "full_name": "Fakultet",
    "name": "Fakultet",
    "owner": None,
    "published": "Publiceret",
    "scope": None,
    "top_level_facet": org_unit_type_facet,
    "user_key": "fak",
    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
}

parent_org_unit = {
    "location": "",
    "name": "Overordnet Enhed",
    "org": org,
    "org_unit_hierarchy": None,
    "org_unit_level": None,
    "org_unit_type": org_unit_type_department,
    "parent": None,
    "time_planning": None,
    "user_key": "root",
    "user_settings": {"orgunit": {}},
    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
    "validity": {"from": "2016-01-01", "to": None},
}
humanities_org_unit = {
    "location": "Overordnet Enhed",
    "name": "Humanistisk fakultet",
    "org": org,
    "org_unit_hierarchy": {
        "example": None,
        "facet": org_unit_hierarchy_facet,
        "full_name": "Selvejet institution",
        "name": "Selvejet institution",
        "owner": None,
        "published": "Publiceret",
        "scope": "TEXT",
        "top_level_facet": org_unit_hierarchy_facet,
        "user_key": "selvejet",
        "uuid": "69de6410-bfe7-bea5-e6cc-376b3302189c",
    },
    "org_unit_level": None,
    "org_unit_type": org_unit_type_institute,
    "parent": parent_org_unit,
    "time_planning": None,
    "user_key": "hum",
    "user_settings": {"orgunit": {}},
    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
    "validity": {"from": "2016-01-01", "to": None},
}
historical_institute_org_unit = {
    "location": "Overordnet Enhed\\Humanistisk fakultet",
    "name": "Historisk Institut",
    "org": org,
    "org_unit_hierarchy": None,
    "org_unit_level": None,
    "org_unit_type": org_unit_type_institute,
    "parent": humanities_org_unit,
    "time_planning": None,
    "user_key": "hist",
    "user_settings": {"orgunit": {}},
    "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
    "validity": {"from": "2016-01-01", "to": "2018-12-31"},
}

future_org_unit = {
    "location": "Overordnet Enhed\\Humanistisk fakultet\\Historisk Institut",
    "name": "Afdeling for Fremtidshistorik",
    "org": org,
    "org_unit_type": org_unit_type_department,
    "org_unit_hierarchy": None,
    "org_unit_level": None,
    "parent": historical_institute_org_unit,
    "time_planning": None,
    "user_key": "frem",
    "user_settings": {"orgunit": {}},
    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
    "validity": {"from": "2016-01-01", "to": "2016-12-31"},
}
present_org_unit = {
    "location": "Overordnet Enhed\\Humanistisk fakultet\\Historisk Institut",
    "name": "Afdeling for Samtidshistorik",
    "org": org,
    "org_unit_hierarchy": None,
    "org_unit_level": None,
    "org_unit_type": org_unit_type_department,
    "parent": historical_institute_org_unit,
    "time_planning": None,
    "user_key": "frem",
    "user_settings": {"orgunit": {}},
    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
    "validity": {"from": "2017-01-01", "to": "2017-12-31"},
}
past_org_unit = {
    "location": "Overordnet Enhed\\Humanistisk fakultet\\Historisk Institut",
    "name": "Afdeling for Fortidshistorik",
    "org": org,
    "org_unit_hierarchy": None,
    "org_unit_level": None,
    "org_unit_type": org_unit_type_department,
    "parent": historical_institute_org_unit,
    "time_planning": None,
    "user_key": "frem",
    "user_settings": {"orgunit": {}},
    "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
    "validity": {"from": "2018-01-01", "to": "2018-12-31"},
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "params, expected",
    [
        ({"validity": "past"}, [future_org_unit]),
        ({"validity": "present"}, [present_org_unit]),
        ({"validity": "future"}, [past_org_unit]),
        (
            {"validity": "past", "at": "2020-01-01"},
            [future_org_unit, present_org_unit, past_org_unit],
        ),
        ({"validity": "present", "at": "2020-01-01"}, []),
        ({"validity": "future", "at": "2020-01-01"}, []),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@set_get_configuration("mora.service.orgunit.get_configuration")
def test_org_unit_temporality(
    service_client: TestClient, params: dict[str, Any], expected: list[dict[str, Any]]
) -> None:
    response = service_client.request(
        "GET",
        "/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48/details/org_unit",
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_create_org_unit_fails_validation_outside_org_unit(
    service_client: TestClient,
) -> None:
    """Validation should fail when date range is outside of org unit
    range"""
    payload = {
        "name": "Fake Corp",
        "parent": {"uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
        "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
        "addresses": [
            {
                "address_type": {
                    "example": "20304060",
                    "name": "Telefon",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                },
                "value": "11 22 33 44",
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                },
                "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
            },
        ],
        "validity": {
            "from": "2010-02-04",
            "to": "2017-10-21",
        },
    }

    expected = {
        "description": "Date range exceeds validity range of associated org unit.",
        "error": True,
        "error_key": "V_DATE_OUTSIDE_ORG_UNIT_RANGE",
        "org_unit_uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
        "status": 400,
        "valid_from": "2016-01-01",
        "valid_to": None,
    }

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 400
    assert response.json() == expected

    response = service_client.request(
        "POST", "/service/ou/create", json=payload, params={"force": 0}
    )
    assert response.status_code == 400
    assert response.json() == expected

    response = service_client.request(
        "POST", "/service/ou/create", json=payload, params={"force": 1}
    )
    assert response.status_code == 201


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_edit_missing_org_unit(service_client: TestClient) -> None:
    req = [
        {
            "type": "org_unit",
            "data": {
                "org_unit_type": {"uuid": "79e15798-7d6d-4e85-8496-dcc8887a1c1a"},
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing uuid",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "uuid",
        "obj": req[0]["data"],
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2010-01-01")
def test_edit_org_unit_earlier_start(service_client: TestClient) -> None:
    """Test setting the start date to something earlier (#23182)"""

    org_unit_uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"

    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "org_unit",
            "data": {
                "uuid": org_unit_uuid,
                "user_key": org_unit_uuid,
                "validity": {
                    "from": "2016-06-01",
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    response = service_client.request(
        "GET", f"/service/ou/{org_unit_uuid}/", params={"at": "2016-06-01"}
    )
    assert response.status_code == 200, "should exist on 2016-06-01"

    response = service_client.request(
        "GET", f"/service/ou/{org_unit_uuid}/", params={"at": "2016-05-31"}
    )
    assert response.status_code == 404, "should not exist before start"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
def test_edit_org_unit_extending_end(service_client: TestClient) -> None:
    unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"

    def check_future_names(*names) -> None:
        response = service_client.request(
            "GET",
            f"/service/ou/{unitid}/details/org_unit",
            params={"validity": "future"},
        )
        assert response.status_code == 200
        result = response.json()

        assert list(names) == [
            (d["name"], d["validity"]["from"], d["validity"]["to"]) for d in result
        ]

    # Prerequisites
    check_future_names(
        ("Afdeling for Samtidshistorik", "2017-01-01", "2017-12-31"),
        ("Afdeling for Fortidshistorik", "2018-01-01", "2018-12-31"),
    )

    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "org_unit",
            "data": {
                "name": "Institut for Vrøvl",
                "uuid": unitid,
                "clamp": True,
                "validity": {
                    "from": "2018-03-01",
                },
            },
        },
    )
    assert response.status_code == 200, "Editing with clamp should succeed"
    assert response.json() == unitid

    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "org_unit",
            "data": {
                "name": "Institut for Sludder",
                "uuid": unitid,
                "clamp": True,
                "validity": {
                    "from": "2018-06-01",
                    "to": "2018-09-30",
                },
            },
        },
    )
    assert response.status_code == 200, "Editing with clamp should succeed"
    assert response.json() == unitid

    check_future_names(
        ("Afdeling for Samtidshistorik", "2017-01-01", "2017-12-31"),
        ("Afdeling for Fortidshistorik", "2018-01-01", "2018-02-28"),
        ("Institut for Vrøvl", "2018-03-01", "2018-05-31"),
        ("Institut for Sludder", "2018-06-01", "2018-09-30"),
        ("Institut for Vrøvl", "2018-10-01", "2018-12-31"),
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2016-01-01")
def test_create_missing_parent(service_client: TestClient) -> None:
    payload = {
        "name": "Fake Corp",
        "parent": {"uuid": "00000000-0000-0000-0000-000000000000"},
        "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
        "addresses": [],
        "validity": {
            "from": "2017-01-01",
            "to": "2018-01-01",
        },
    }

    response = service_client.request("POST", "/service/ou/create", json=payload)
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
def test_edit_time_planning(service_client: TestClient) -> None:
    org_unit_uuid = "85715fc7-925d-401b-822d-467eb4b163b6"

    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "org_unit",
            "data": {
                "time_planning": {
                    "uuid": org_unit_type_faculty["uuid"],
                },
                "uuid": org_unit_uuid,
                "validity": {
                    "from": "2017-01-01",
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == org_unit_uuid

    response = service_client.request(
        "GET",
        f"/service/ou/{org_unit_uuid}/details/org_unit",
        params={"validity": "present"},
    )
    assert response.status_code == 200
    result = one(response.json())

    assert result["time_planning"] == org_unit_type_faculty


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload, expected",
    [
        # Should fail validation when trying to move an org unit to one of its children.
        (
            {
                "type": "org_unit",
                "data": {
                    "parent": {"uuid": "85715fc7-925d-401b-822d-467eb4b163b6"},
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "validity": {
                        "from": "2017-07-01",
                    },
                },
            },
            {
                "description": "Org unit cannot be moved to one of its own child units",
                "error": True,
                "error_key": "V_ORG_UNIT_MOVE_TO_CHILD",
                "org_unit_uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "status": 400,
            },
        ),
        # Verify that we cannot create cycles when moving organisational units
        (
            {
                "type": "org_unit",
                "data": {
                    "parent": {"uuid": "85715fc7-925d-401b-822d-467eb4b163b6"},  # child
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",  # parent
                    "validity": {
                        "from": "2018-01-01",
                    },
                },
            },
            {
                "description": "Org unit cannot be moved to one of its own child units",
                "error": True,
                "error_key": "V_ORG_UNIT_MOVE_TO_CHILD",
                "status": 400,
                "org_unit_uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",  # parent
            },
        ),
        # Verify that we cannot move units to places that do not exist
        (
            {
                "type": "org_unit",
                "data": {
                    "parent": {
                        "uuid": "00000000-0000-0000-0000-000000000001",
                    },
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
            {
                "description": "Org unit not found.",
                "error": True,
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": "00000000-0000-0000-0000-000000000001",
                "status": 404,
            },
        ),
    ],
)
def test_move_fail_validation(
    service_client: TestClient, payload: dict[str, Any], expected: dict[str, Any]
) -> None:
    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == expected["status"]
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_edit_org_unit_should_fail_validation_when_end_before_start(
    service_client: TestClient,
) -> None:
    """Should fail validation when trying to edit an org unit with the
    to-time being before the from-time"""

    org_unit_uuid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    req = {
        "type": "org_unit",
        "data": {
            "parent": {"uuid": "85715fc7-925d-401b-822d-467eb4b163b6"},
            "uuid": org_unit_uuid,
            "validity": {
                "from": "2017-07-01",
                "to": "2015-07-01",
            },
        },
    }
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 400
    assert response.json() == {
        "description": "End date is before start date.",
        "error": True,
        "error_key": "V_END_BEFORE_START",
        "status": 400,
        "obj": req["data"],
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "inactive_validity, expected_validity",
    [
        # Test new payload, which includes both "from" and "to" dates
        (
            # The payload asks for an *inactive* period from Jan 1, 2017 to
            # Jan 1, 2018.
            {"from": "2017-01-01", "to": "2018-01-01"},
            # Upon termination, the org unit will have an *active* period from
            # Jan 1, 2016 to Dec 31, 2016 (the day before its termination.)
            {"from": "2016-01-01", "to": "2016-12-31"},
        ),
        # Test old payload, which only has a "to" date
        (
            # The payload asks for an *inactive* period beginning infinitely
            # far in the past and ending on Oct 21, 2016.
            {"to": "2016-10-21"},
            # Upon termination, the org unit will have an *active* period from
            # Jan 1, 2016 to Oct 21, 2016 (the day of its termination.)
            {"from": "2016-01-01", "to": "2016-10-21"},
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@set_get_configuration("mora.service.orgunit.get_configuration")
def test_terminate_org_unit(
    service_client: TestClient,
    inactive_validity: dict[str, str],
    expected_validity: dict[str, str],
) -> None:
    unitid = "85715fc7-925d-401b-822d-467eb4b163b6"
    payload = {"validity": inactive_validity}

    response = service_client.request(
        "POST", f"/service/ou/{unitid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == unitid

    response = service_client.request(
        "GET", f"/service/ou/{unitid}/details/org_unit", params={"validity": "past"}
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "location": "Overordnet Enhed\\Humanistisk fakultet",
            "name": "Filosofisk Institut",
            "org": org,
            "org_unit_hierarchy": None,
            "org_unit_level": None,
            "org_unit_type": org_unit_type_institute,
            "parent": humanities_org_unit,
            "time_planning": None,
            "user_key": "fil",
            "user_settings": {"orgunit": {}},
            "uuid": unitid,
            "validity": expected_validity,
        }
    ]

    # Verify that we are no longer able to see org unit
    response = service_client.request(
        "GET", f"/service/ou/{unitid}/details/org_unit", params={"validity": "present"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "validity",
    [
        # Test new payload, which includes both "from" and "to" dates
        {"from": "2017-01-01", "to": "2018-01-01"},
        # Test old payload, which only has a "to" date
        {"to": "2016-10-21"},
    ],
)
def test_terminate_org_unit_invalid_uuid(
    service_client: TestClient, validity: dict[str, str]
) -> None:
    unitid = "00000000-0000-0000-0000-000000000000"

    response = service_client.request(
        "POST", f"/service/ou/{unitid}/terminate", json={"validity": validity}
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": True,
        "error_key": "E_ORG_UNIT_NOT_FOUND",
        "description": "Org unit not found.",
        "org_unit_uuid": unitid,
        "status": 404,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "org_unit_uuid, validity, expected_error_response",
    [
        # Test new payload, which includes both "from" and "to" dates
        (
            # org unit uuid
            "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            # payload
            {"from": "2017-01-01", "to": "2018-01-01"},
            # expected error response
            expected_error_response("V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES"),
        ),
        (
            # org unit uuid
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            # payload
            {"from": "2017-01-01", "to": "2018-01-01"},
            # expected error response
            expected_error_response(
                "V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES",
                roles="Adresse, Engagement, Leder, Relateret Enhed, Rollebinding, Tilknytning",
                child_count=2,
            ),
        ),
        # Test old payload, which only has a "to" date
        (
            # org unit uuid
            "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            # payload
            {"to": "2017-01-01"},
            # expected error response
            expected_error_response("V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES"),
        ),
        (
            # org unit uuid
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            # payload
            {"to": "2017-01-01"},
            # expected error response
            expected_error_response(
                "V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES",
                roles="Adresse, Engagement, Leder, Relateret Enhed, Rollebinding, Tilknytning",
                child_count=2,
            ),
        ),
        (
            # org unit uuid
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            # payload
            {"to": "2018-12-31"},
            # expected error response
            expected_error_response(
                "V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES",
                roles="Adresse, Engagement, Leder, Relateret Enhed, Rollebinding, Tilknytning",
                child_count=1,
            ),
        ),
    ],
)
def test_terminate_org_unit_active_children_and_roles(
    service_client: TestClient,
    org_unit_uuid: str,
    validity: dict[str, str],
    expected_error_response: dict[str, Any],
) -> None:
    response = service_client.request(
        "POST", f"/service/ou/{org_unit_uuid}/terminate", json={"validity": validity}
    )
    assert response.status_code == 400
    assert response.json() == {"error": True, "status": 400, **expected_error_response}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_terminate_org_unit_validations_other(service_client: TestClient) -> None:
    unitid_a = "85715fc7-925d-401b-822d-467eb4b163b6"
    unitid_b = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    response = service_client.request(
        "POST",
        f"/service/ou/{unitid_a}/terminate",
        json={"validity": {"to": "2018-12-31"}},
    )
    assert response.status_code == 200
    assert response.json() == unitid_a

    response = service_client.request(
        "POST",
        f"/service/ou/{unitid_b}/terminate",
        json={
            "validity": {
                # inclusion of timestamp is deliberate
                "to": "2018-12-31T00:00:00+01"
            }
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "status": 400,
        **expected_error_response("V_TERMINATE_UNIT_WITH_ROLES"),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "org_unit_uuid, validity, expected_error_response",
    [
        (
            # org unit uuid
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            # payload
            {"to": "1999-12-31"},
            # expected error response
            expected_error_response(
                "V_DATE_OUTSIDE_ORG_UNIT_RANGE",
                org_unit_uuid="9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                valid_from="2016-01-01",
                valid_to=None,
            ),
        ),
        (
            # org unit uuid
            "04c78fc2-72d2-4d02-b55f-807af19eac48",
            # payload
            {"to": "2099-12-31"},
            # expected error response
            expected_error_response(
                "V_DATE_OUTSIDE_ORG_UNIT_RANGE",
                org_unit_uuid="04c78fc2-72d2-4d02-b55f-807af19eac48",
                valid_from="2016-01-01",
                valid_to="2018-12-31",
            ),
        ),
    ],
)
def test_terminate_org_unit_date_outside_org_unit_range(
    service_client: TestClient,
    org_unit_uuid: str,
    validity: dict[str, str],
    expected_error_response: dict[str, Any],
) -> None:
    response = service_client.request(
        "POST", f"/service/ou/{org_unit_uuid}/terminate", json={"validity": validity}
    )
    assert response.status_code == 400
    assert response.json() == {"error": True, "status": 400, **expected_error_response}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize("path, expected", util.get_fixture("test_trees.json").items())
def test_tree(service_client: TestClient, path: str, expected: dict[str, Any]) -> None:
    response = service_client.request("GET", path)
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_edit_org_unit_60582(graphapi_post):
    CREATE_ORG_UNIT = "mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) { org_unit_create(input: $input) { uuid } }"

    # create parent
    response = graphapi_post(
        CREATE_ORG_UNIT,
        {
            "input": {
                "validity": {"from": "2023-01-01", "to": "2026-01-01"},
                "name": "Parent",
                "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
            }
        },
    )
    assert response.errors is None
    parent_uuid = response.data["org_unit_create"]["uuid"]

    # create child
    child_input = {
        "input": {
            "validity": {"from": "2024-01-01", "to": "2025-01-01"},
            "name": "Child",
            "parent": parent_uuid,
            "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
        }
    }
    response = graphapi_post(
        CREATE_ORG_UNIT,
        child_input,
    )
    assert response.errors is None
    child_uuid = response.data["org_unit_create"]["uuid"]

    # edit child to exceed parent validity range
    child_input["input"]["validity"]["to"] = "2027-01-01"
    child_input["input"]["uuid"] = child_uuid
    response = graphapi_post(
        "mutation EditOrgUnit($input: OrganisationUnitUpdateInput!) { org_unit_update(input: $input) { uuid } }",
        child_input,
    )
    # expect this to fail, since child can't exceed parents validity range
    assert response.errors is not None
    assert response.errors[0]["message"] == "ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_future_children(graphapi_post):
    CREATE_ORG_UNIT = """
    mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
      org_unit_create(input: $input) {
        uuid
      }
    }
    """

    # Create future parent
    response = graphapi_post(
        CREATE_ORG_UNIT,
        {
            "input": {
                "validity": {"from": "2100-01-01"},
                "name": "parent",
                "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
            }
        },
    )
    assert response.errors is None
    parent_uuid = response.data["org_unit_create"]["uuid"]

    # Create future child
    response = graphapi_post(
        CREATE_ORG_UNIT,
        {
            "input": {
                "validity": {"from": "2100-01-01"},
                "name": "child",
                "parent": parent_uuid,
                "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
            }
        },
    )
    assert response.errors is None
    child_uuid = response.data["org_unit_create"]["uuid"]

    # Read parent's children
    response = graphapi_post(
        """
        query OrgUnitChildren($uuid: [UUID!], $fromDate: DateTime) {
          org_units(filter: { uuids: $uuid, from_date: $fromDate }) {
            objects {
              validities {
                child_count(filter: { from_date: $fromDate })
                has_children(filter: { from_date: $fromDate })
                children(filter: { from_date: $fromDate }) {
                  uuid
                }
              }
            }
          }
        }
        """,
        {
            "uuid": parent_uuid,
            "fromDate": "2100-01-01",
        },
    )
    assert response.errors is None
    assert response.data == {
        "org_units": {
            "objects": [
                {
                    "validities": [
                        {
                            "child_count": 1,
                            "children": [{"uuid": child_uuid}],
                            "has_children": True,
                        }
                    ]
                }
            ]
        }
    }
