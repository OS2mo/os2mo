# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import timezone
from unittest.mock import AsyncMock

import freezegun
import oio_rest.custom_exceptions as loraexc
import pytest
from mora import exceptions
from mora import lora
from mora import util as mora_util
from oio_rest.organisation import Bruger
from oio_rest.organisation import OrganisationEnhed


@freezegun.freeze_time("2010-06-01", tz_offset=2)
async def test_get_effects(monkeypatch) -> None:
    async def arrange(_):
        return {
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
                                        for t1, t2, v in (
                                            (
                                                "01-01-1950",
                                                "01-01-2100",
                                                "Aktiv",
                                            ),
                                            (
                                                "01-01-2100",
                                                "01-01-2300",
                                                "Inaktiv",
                                            ),
                                            (
                                                "01-01-2300",
                                                "01-01-2500",
                                                "Aktiv",
                                            ),
                                            (
                                                "01-01-2500",
                                                "01-01-2700",
                                                "Inaktiv",
                                            ),
                                            (
                                                "01-01-2700",
                                                "01-01-2900",
                                                "Aktiv",
                                            ),
                                            (
                                                "01-01-2900",
                                                "01-01-3100",
                                                "Inaktiv",
                                            ),
                                            (
                                                "01-01-3100",
                                                "01-01-3300",
                                                "Aktiv",
                                            ),
                                        )
                                    ]
                                },
                            }
                        ],
                    }
                ]
            ]
        }

    monkeypatch.setattr(OrganisationEnhed, "get_objects_direct", arrange)

    c = lora.Connector(validity="future")

    assert [
        (
            "2100-01-01 00:00:00+01:00",
            "2300-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2100-01-01T00:00:00+01:00",
                                "to": "2300-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2300-01-01 00:00:00+01:00",
            "2500-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2300-01-01T00:00:00+01:00",
                                "to": "2500-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2500-01-01 00:00:00+01:00",
            "2700-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2500-01-01T00:00:00+01:00",
                                "to": "2700-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2700-01-01 00:00:00+01:00",
            "2900-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2700-01-01T00:00:00+01:00",
                                "to": "2900-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2900-01-01 00:00:00+01:00",
            "3100-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2900-01-01T00:00:00+01:00",
                                "to": "3100-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "3100-01-01 00:00:00+01:00",
            "3300-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "3100-01-01T00:00:00+01:00",
                                "to": "3300-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
    ] == [
        (str(start), str(end), entry)
        for (start, end, entry) in (
            await c.organisationenhed.get_effects(
                "00000000-0000-0000-0000-000000000000",
                relevant={"tilstande": ("organisationenhedgyldighed",)},
            )
        )
    ]


@pytest.mark.parametrize(
    "lora_exception,status_out,error_key",
    [
        (loraexc.BadRequestException, 400, "E_INVALID_INPUT"),
        (loraexc.UnauthorizedException, 401, "E_UNAUTHORIZED"),
        (loraexc.AuthorizationFailedException, 403, "E_FORBIDDEN"),
        (Exception, 500, "E_UNKNOWN"),
    ],
)
async def test_errors_json(
    monkeypatch, lora_exception: Exception, status_out: int, error_key: str
) -> None:
    async def arrange(*_, **__):
        raise lora_exception("go away")

    monkeypatch.setattr(OrganisationEnhed, "get_objects_direct", arrange)

    with pytest.raises(exceptions.HTTPException) as ctxt:
        await lora.Connector().organisationenhed.get("42")

    assert ctxt.value.detail == {
        "error": True,
        "status": status_out,
        "error_key": error_key,
        "description": "go away",
    }


async def test_finding_nothing(monkeypatch) -> None:
    monkeypatch.setattr(
        OrganisationEnhed, "get_objects_direct", AsyncMock(return_value={"results": []})
    )
    assert (await lora.Connector().organisationenhed.get("42")) is None


@freezegun.freeze_time("2001-01-01 15:30:00")
async def test_get_effects_2(monkeypatch) -> None:
    arrange = {
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
                                    for t1, t2, v in (
                                        (
                                            "01-01-1950",
                                            "01-01-2100",
                                            "Aktiv",
                                        ),
                                        (
                                            "01-01-2100",
                                            "01-01-2300",
                                            "Inaktiv",
                                        ),
                                        (
                                            "01-01-2300",
                                            "01-01-2500",
                                            "Aktiv",
                                        ),
                                        (
                                            "01-01-2500",
                                            "01-01-2700",
                                            "Inaktiv",
                                        ),
                                        (
                                            "01-01-2700",
                                            "01-01-2900",
                                            "Aktiv",
                                        ),
                                        (
                                            "01-01-2900",
                                            "01-01-3100",
                                            "Inaktiv",
                                        ),
                                        (
                                            "01-01-3100",
                                            "01-01-3300",
                                            "Aktiv",
                                        ),
                                    )
                                ]
                            },
                        }
                    ],
                }
            ]
        ]
    }

    get_objects = AsyncMock(return_value=arrange)
    monkeypatch.setattr(OrganisationEnhed, "get_objects_direct", get_objects)

    c = lora.Connector(validity="future")

    assert [
        (
            "2100-01-01 00:00:00+01:00",
            "2300-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2100-01-01T00:00:00+01:00",
                                "to": "2300-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2300-01-01 00:00:00+01:00",
            "2500-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2300-01-01T00:00:00+01:00",
                                "to": "2500-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2500-01-01 00:00:00+01:00",
            "2700-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2500-01-01T00:00:00+01:00",
                                "to": "2700-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2700-01-01 00:00:00+01:00",
            "2900-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2700-01-01T00:00:00+01:00",
                                "to": "2900-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "2900-01-01 00:00:00+01:00",
            "3100-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2900-01-01T00:00:00+01:00",
                                "to": "3100-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
        (
            "3100-01-01 00:00:00+01:00",
            "3300-01-01 00:00:00+01:00",
            {
                "tilstande": {
                    "organisationenhedgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "3100-01-01T00:00:00+01:00",
                                "to": "3300-01-01T00:00:00+01:00",
                            },
                        }
                    ]
                }
            },
        ),
    ] == [
        (str(start), str(end), entry)
        for (start, end, entry) in (
            await c.organisationenhed.get_effects(
                "00000000-0000-0000-0000-000000000000",
                relevant={"tilstande": ("organisationenhedgyldighed",)},
            )
        )
    ]

    get_objects.assert_awaited_once_with(
        [
            ("virkningfra", "2001-01-01T16:30:00+01:00"),
            ("virkningtil", "infinity"),
            ("konsolider", "True"),
            ("uuid", "00000000-0000-0000-0000-000000000000"),
        ]
    )


async def test_noop_update_returns_null(monkeypatch) -> None:
    # A "no-op" update in LoRa returns a response with an error message,
    # but no "uuid" key.
    uuid = "cbd4d304-9466-4524-b8e6-aa4a5a5cb787"

    async def patch_object(_, __):
        raise loraexc.BadRequestException(
            "ERROR:  Aborted updating bruger with id [cbd4d304-9466-4524-b8e6-aa4a5a5cb787] as the given data, does not give raise to a new registration. Aborted reg: ..."
        )

    monkeypatch.setattr(Bruger, "patch_object_direct", patch_object)
    # Assert that `Scope.update` tolerates the missing 'uuid' key in the
    # LoRa response, and instead just returns the original UUID back to its
    # caller.
    c = lora.Connector()
    same_uuid = await c.bruger.update({}, uuid)
    assert uuid == same_uuid


async def test_actual_update_returns_uuid(monkeypatch) -> None:
    # A normal update in LoRa returns a response with a 'uuid' key which
    # matches the object that was updated.
    uuid = "cbd4d304-9466-4524-b8e6-aa4a5a5cb787"
    monkeypatch.setattr(
        Bruger, "patch_object_direct", AsyncMock(return_value={"uuid": uuid})
    )
    # Assert that `Scope.update` parses the JSON response and returns the
    # value of the 'uuid' key to its caller.
    c = lora.Connector()
    updated_uuid = await c.bruger.update({}, uuid)
    assert uuid == updated_uuid


async def test_update_returns_nothing_on_lora_404(monkeypatch) -> None:
    # Updating a nonexistent LoRa object returns a 404 status code, which
    # should not be converted into a MO exception.
    uuid = "00000000-0000-0000-0000-000000000000"

    async def patch_object(_, __):
        raise loraexc.NotFoundException()

    monkeypatch.setattr(Bruger, "patch_object_direct", patch_object)

    # Assert that `Scope.update` does not raise an exception nor return a
    # UUID in this case.
    c = lora.Connector()
    response = await c.bruger.update({}, uuid)
    assert response is None


@pytest.mark.parametrize(
    "validity_literal,now,expected",
    [
        (
            "past",
            date(2023, 1, 5),
            (
                datetime.min.replace(tzinfo=timezone.utc),
                datetime(2023, 1, 5, 0, 0, 0, 0),
            ),
        ),
        (
            "present",
            date(2023, 1, 5),
            (
                datetime(2023, 1, 5, 0, 0, 0, 0),
                datetime(2023, 1, 5, 0, 0, 0, 1),
            ),
        ),
        (
            "present",
            datetime(2023, 1, 5, 0, 0, 0, 0),
            (
                datetime(2023, 1, 5, 0, 0, 0, 0),
                datetime(2023, 1, 5, 0, 0, 0, 1),
            ),
        ),
        (
            "future",
            date(2023, 1, 5),
            (
                datetime(2023, 1, 5, 0, 0, 0, 0),
                datetime.max.replace(tzinfo=timezone.utc),
            ),
        ),
    ],
)
async def test_validity_tuple(
    validity_literal: lora.ValidityLiteral,
    now: date | datetime,
    expected: tuple[datetime, datetime],
):
    result = lora.validity_tuple(validity_literal, now=now)
    assert result == expected
