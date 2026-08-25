# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from mora import lora
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import UnitDetails
from mora.service.orgunit import get_one_orgunit
from oio_rest.organisation import OrganisationEnhed
from tests import util


@pytest.mark.freeze_time("2018-03-15")
async def test_unit_past(monkeypatch, service_client: TestClient) -> None:
    unitid = "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc"

    reg = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": "IDR\u00c6TSPARK",
                    "enhedsnavn": "Ballerup Idr\u00e6tspark",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ]
        },
        "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
        "fratidspunkt": {
            "graenseindikator": True,
            "tidsstempeldatotid": "2018-03-09T14:38:45.310653+01:00",
        },
        "livscykluskode": "Rettet",
        "relationer": {
            "adresser": [
                {
                    "objekttype": "a8c8fe66-2ab1-46ed-ba99-ed05e855d65f",
                    "uuid": "9ab45e95-a42a-47c0-b284-e5d2377fc429",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "objekttype": "80764a2f-6a7b-492c-92d9-96d24ac845ea",
                    "urn": "urn:mailto:tbri@balk.dk",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "enhedstype": [
                {
                    "uuid": "547e6946-abdb-4dc2-ad99-b6042e05a7e4",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "overordnet": [
                {
                    "uuid": "9f42976b-93be-4e0b-9a25-0dcb8af2f6b4",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilhoerer": [
                {
                    "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
            "tilknyttedeenheder": [
                {
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    }
                }
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from": "1993-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
                {
                    "gyldighed": "Inaktiv",
                    "virkning": {
                        "from": "-infinity",
                        "from_included": True,
                        "to": "1993-01-01 00:00:00+01",
                        "to_included": False,
                    },
                },
            ]
        },
        "tiltidspunkt": {"tidsstempeldatotid": "infinity"},
    }

    route = AsyncMock(
        return_value={
            "results": [
                [
                    {
                        "id": "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc",
                        "registreringer": [
                            reg,
                        ],
                    }
                ]
            ]
        }
    )

    monkeypatch.setattr(OrganisationEnhed, "get_objects_direct", route)

    mo_url = f"/service/ou/{unitid}/details/org_unit?validity=past"
    async with util.patch_query_args({"validity": "past"}):
        response = service_client.request("GET", mo_url)
        assert response.status_code == 200
        assert response.json() == []

    route.assert_awaited_with(
        [
            ("virkningfra", "-infinity"),
            ("virkningtil", "2018-03-15T01:00:00+01:00"),
            ("konsolider", "True"),
            ("uuid", unitid),
        ]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.patch_query_args()
async def test_get_one_orgunit_with_association_count() -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector,
        "2874e1dc-85e6-4269-823a-e1125484dfd3",
        count_related={"association": AssociationReader},
    )
    assert orgunit is not None
    assert "association_count" in orgunit


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "details,expected_keys",
    [
        (
            UnitDetails.NCHILDREN,
            {"uuid", "name", "user_key", "validity", "child_count"},
        ),
        (UnitDetails.PATH, {"uuid", "name", "user_key", "validity", "location"}),
    ],
)
@util.patch_query_args()
async def test_details(details: UnitDetails, expected_keys: set[str]) -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector, "2874e1dc-85e6-4269-823a-e1125484dfd3", details=details
    )
    assert orgunit is not None
    assert set(orgunit.keys()) == expected_keys
