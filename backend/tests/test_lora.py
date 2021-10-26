# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import re

import freezegun
import mora.async_util
import tests.cases
from aioresponses import aioresponses
from mora import config
from mora import exceptions
from mora import lora
from mora import util as mora_util
from more_itertools import last
from more_itertools import one
from parameterized import parameterized
from yarl import URL

from . import util


@freezegun.freeze_time("2010-06-01", tz_offset=2)
class Tests(tests.cases.TestCase):
    @util.MockAioresponses()
    def test_get_effects(self, m):
        lora_url = config.get_settings().lora_url
        url = URL(f"{lora_url}organisation/organisationenhed")
        m.get(
            url,
            payload={
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
                                            for t1, t2, v in [
                                                ("01-01-1950", "01-01-2100", "Aktiv"),
                                                ("01-01-2100", "01-01-2300", "Inaktiv"),
                                                ("01-01-2300", "01-01-2500", "Aktiv"),
                                                ("01-01-2500", "01-01-2700", "Inaktiv"),
                                                ("01-01-2700", "01-01-2900", "Aktiv"),
                                                ("01-01-2900", "01-01-3100", "Inaktiv"),
                                                ("01-01-3100", "01-01-3300", "Aktiv"),
                                            ]
                                        ]
                                    },
                                }
                            ],
                        }
                    ]
                ]
            },
        )

        c = lora.Connector(validity="future")

        self.assertEqual(
            [
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
            ],
            [
                (str(start), str(end), entry)
                for start, end, entry in (
                    mora.async_util.async_to_sync(c.organisationenhed.get_effects)(
                        "00000000-0000-0000-0000-000000000000",
                        relevant={
                            "tilstande": ("organisationenhedgyldighed",),
                        },
                    )
                )
            ],
        )

        call_args = one(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2010-06-01T02:00:00+02:00",
                "virkningtil": "infinity",
                "konsolider": "True",
            },
        )

    @parameterized.expand(
        [
            (400, 400, "E_INVALID_INPUT"),
            (401, 401, "E_UNAUTHORIZED"),
            (403, 403, "E_FORBIDDEN"),
            (426, 500, "E_UNKNOWN"),
            (500, 500, "E_UNKNOWN"),
        ]
    )
    @util.MockAioresponses()
    def test_errors_json(self, status_in, status_out, error_key, m):
        c = lora.Connector()
        url = URL("http://mox/organisation/organisationenhed")

        m.get(
            url,
            payload={
                "message": "go away",
            },
            status=status_in,
        )

        with self.assertRaises(exceptions.HTTPException) as ctxt:
            mora.async_util.async_to_sync(c.organisationenhed.get)("42")

        call_args = last(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["42"],
                "virkningfra": "2010-06-01T02:00:00+02:00",
                "virkningtil": "2010-06-01T02:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

        self.assertEqual(
            {
                "error": True,
                "status": status_out,
                "error_key": error_key,
                "description": "go away",
            },
            ctxt.exception.detail,
        )

    @parameterized.expand(
        [
            (400, 400, "E_INVALID_INPUT"),
            (401, 401, "E_UNAUTHORIZED"),
            (403, 403, "E_FORBIDDEN"),
            (426, 500, "E_UNKNOWN"),
            (500, 500, "E_UNKNOWN"),
        ]
    )
    @util.MockAioresponses()
    def test_errors_text(self, status_in, status_out, error_key, m):
        c = lora.Connector()
        url = URL("http://mox/organisation/organisationenhed")

        m.get(
            url,
            body="I hate you",
            status=status_in,
        )

        with self.assertRaises(exceptions.HTTPException) as ctxt:
            mora.async_util.async_to_sync(c.organisationenhed.get)("42")

        call_args = last(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["42"],
                "virkningfra": "2010-06-01T02:00:00+02:00",
                "virkningtil": "2010-06-01T02:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

        self.assertEqual(
            {
                "error": True,
                "status": status_out,
                "error_key": error_key,
                "description": "I hate you",
            },
            ctxt.exception.detail,
        )

    @util.MockAioresponses()
    def test_error_debug(self, m):
        # with util.override_lora_url():
        url = URL("http://mox/organisation/organisationenhed")
        m.get(
            url,
            payload={
                "message": "go away",
                "something": "other",
            },
            status=500,
        )

        with self.assertRaises(exceptions.HTTPException) as ctxt:
            mora.async_util.async_to_sync(lora.Connector().organisationenhed.get)("42")

        call_args = one(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["42"],
                "virkningfra": "2010-06-01T02:00:00+02:00",
                "virkningtil": "2010-06-01T02:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

        self.assertEqual(
            {
                "error": True,
                "status": 500,
                "error_key": "E_UNKNOWN",
                "description": "go away",
            },
            ctxt.exception.detail,
        )

    @util.MockAioresponses()
    def test_finding_nothing(self, m):
        c = lora.Connector()
        url = URL("http://mox/organisation/organisationenhed")
        m.get(
            url,
            payload={"results": []},
        )

        self.assertIsNone(mora.async_util.async_to_sync(c.organisationenhed.get)("42"))
        call_args = one(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["42"],
                "virkningfra": "2010-06-01T02:00:00+02:00",
                "virkningtil": "2010-06-01T02:00:00.000001+02:00",
                "konsolider": "True",
            },
        )

    @freezegun.freeze_time("2001-01-01", tz_offset=1)
    @aioresponses()
    def test_get_effects_2(self, m):
        lora_url = config.get_settings().lora_url
        url = URL(f"{lora_url}organisation/organisationenhed")
        m.get(
            url,
            payload={
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
                                            for t1, t2, v in [
                                                ("01-01-1950", "01-01-2100", "Aktiv"),
                                                ("01-01-2100", "01-01-2300", "Inaktiv"),
                                                ("01-01-2300", "01-01-2500", "Aktiv"),
                                                ("01-01-2500", "01-01-2700", "Inaktiv"),
                                                ("01-01-2700", "01-01-2900", "Aktiv"),
                                                ("01-01-2900", "01-01-3100", "Inaktiv"),
                                                ("01-01-3100", "01-01-3300", "Aktiv"),
                                            ]
                                        ]
                                    },
                                }
                            ],
                        }
                    ]
                ]
            },
        )

        c = lora.Connector(validity="future")

        self.assertEqual(
            [
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
            ],
            [
                (str(start), str(end), entry)
                for start, end, entry in (
                    mora.async_util.async_to_sync(c.organisationenhed.get_effects)(
                        "00000000-0000-0000-0000-000000000000",
                        relevant={
                            "tilstande": ("organisationenhedgyldighed",),
                        },
                    )
                )
            ],
        )

        call_args = one(m.requests["GET", url])
        self.assertEqual(
            call_args.kwargs["json"],
            {
                "uuid": ["00000000-0000-0000-0000-000000000000"],
                "virkningfra": "2001-01-01T01:00:00+01:00",
                "virkningtil": "infinity",
                "konsolider": "True",
            },
        )

    def test_raise_on_status_detects_noop_change(self):
        status_code = 400
        msg_noop = (
            "ERROR:  Aborted updating bruger with id "
            "[cbd4d304-9466-4524-b8e6-aa4a5a5cb787] as the given data, does "
            "not give raise to a new registration. Aborted reg: ..."
        )
        msg_other = "ERROR: Some other error"
        # Assert the 'noop' error does not raise an exception
        self.assertIsNone(lora.raise_on_status(status_code, msg_noop))
        # Assert that any other error does raise an exception
        with self.assertRaises(exceptions.HTTPException) as ctxt:
            lora.raise_on_status(status_code, msg_other)
        self.assertEqual(
            {
                "error": True,
                "status": status_code,
                "error_key": "E_INVALID_INPUT",
                "description": msg_other,
            },
            ctxt.exception.detail,
        )

    @util.MockAioresponses()
    def test_noop_update_returns_null(self, m):
        # A "no-op" update in LoRa returns a response with an error message,
        # but no "uuid" key.
        uuid = "cbd4d304-9466-4524-b8e6-aa4a5a5cb787"
        m.patch(
            re.compile(r".*/organisation/bruger/" + uuid),
            payload={
                "message": "ERROR:  Aborted updating bruger with id "
                "[cbd4d304-9466-4524-b8e6-aa4a5a5cb787] as the given data, does "
                "not give raise to a new registration. Aborted reg: ..."
            },
        )
        # Assert that `Scope.update` tolerates the missing 'uuid' key in the
        # LoRa response, and instead just returns the original UUID back to its
        # caller.
        c = lora.Connector()
        same_uuid = mora.async_util.async_to_sync(c.bruger.update)({}, uuid)
        self.assertEqual(uuid, same_uuid)

    @util.MockAioresponses()
    def test_actual_update_returns_uuid(self, m):
        # A normal update in LoRa returns a response with a 'uuid' key which
        # matches the object that was updated.
        uuid = "cbd4d304-9466-4524-b8e6-aa4a5a5cb787"
        m.patch(re.compile(r".*/organisation/bruger/" + uuid), payload={"uuid": uuid})
        # Assert that `Scope.update` parses the JSON response and returns the
        # value of the 'uuid' key to its caller.
        c = lora.Connector()
        updated_uuid = mora.async_util.async_to_sync(c.bruger.update)({}, uuid)
        self.assertEqual(uuid, updated_uuid)

    @util.MockAioresponses()
    def test_update_returns_nothing_on_lora_404(self, m):
        # Updating a nonexistent LoRa object returns a 404 status code, which
        # should not be converted into a MO exception.
        uuid = "00000000-0000-0000-0000-000000000000"
        m.patch(re.compile(r".*/organisation/bruger/" + uuid), status=404)
        # Assert that `Scope.update` does not raise an exception nor return a
        # UUID in this case.
        c = lora.Connector()
        response = mora.async_util.async_to_sync(c.bruger.update)({}, uuid)
        self.assertIsNone(response)
