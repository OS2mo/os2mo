# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from unittest import mock

from starlette.requests import Request
from starlette.responses import JSONResponse

import tests.cases
from mora import app


class AsyncTests(tests.cases.IsolatedAsyncioTestCase):
    async def test_fallback_handler(self):
        resp = await app.fallback_handler(mock.MagicMock(), ValueError("go away"))

        self.assertIsInstance(resp, JSONResponse)
        self.assertEqual(500, resp.status_code)
        self.assertEqual(
            b'{"error":true,"description":"go away",'
            b'"status":500,"error_key":"E_UNKNOWN"}',
            resp.body,
        )


class Tests(tests.cases.TestCase):
    def test_failing_service(self):
        self.assertRequestResponse(
            "/service/kaflaflibob",
            {
                "error": True,
                "error_key": "E_NO_SUCH_ENDPOINT",
                "description": "No such endpoint.",
                "status": 404,
            },
            status_code=404,
        )


class PatchedAppTests(tests.cases.TestCase):
    fb = app.fallback_handler

    def setUp(self):
        self.mock_fallback = mock.AsyncMock()
        app.fallback_handler = self.mock_fallback
        super().setUp()

    def tearDown(self):
        app.fallback_handler = self.fb
        super().tearDown()

    @mock.patch("mora.common.get_connector")
    def test_exception_handling(self, p):
        vErr = ValueError("go away")
        p.side_effect = vErr
        with self.assertRaises(ValueError):
            self.assertRequestResponse(
                "/service/ou/00000000-0000-0000-0000-000000000000/",
                {
                    "error": True,
                    "error_key": "E_UNKNOWN",
                    "description": "go away",
                    "status": 500,
                },
                status_code=500,
            )

        calls = self.mock_fallback.call_args_list
        self.assertEqual(1, len(calls))
        args = calls[0][0]
        kwargs = calls[0][1]
        self.assertEqual(2, len(args))
        self.assertEqual({}, kwargs)
        self.assertIsInstance(args[0], Request)
        self.assertIsInstance(args[1], ValueError)
        self.assertEqual(str(vErr), str(args[1]))
