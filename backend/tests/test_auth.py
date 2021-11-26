# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import freezegun
import pytest

import tests.cases
from . import util

IDP_URL = "mock://idp"

EMPL_URL = (
    "http://mox/organisation/bruger"
    "?virkningtil=2001-01-01T00%3A00%3A00.000001%2B01%3A00"
    "&uuid=d90862d0-c890-4183-bbc6-c403b125bd5a"
    "&virkningfra=2001-01-01T00%3A00%3A00%2B01%3A00"
    "&konsolider=True"
)


@freezegun.freeze_time("2001-01-01")
class MockTests(tests.cases.TestCase):
    @util.MockAioresponses(passthrough=["http://localhost"])
    def test_access_denied(self, mock):
        mock.get(
            EMPL_URL,
            status=401,
            payload={
                "message": "No Authorization header present",
            },
        )

        self.assertRequestResponse(
            "/service/e/d90862d0-c890-4183-bbc6-c403b125bd5a/",
            {
                "error": True,
                "error_key": "E_UNAUTHORIZED",
                "description": "No Authorization header present",
                "status": 401,
            },
            status_code=401,
        )

    @pytest.mark.xfail(reason="need auth")
    def test_get_user_returns_username_from_attr(self):
        self.app.config["SAML_USERNAME_ATTR"] = "whatever"
        self.app.config["SAML_USERNAME_FROM_NAMEID"] = False

        with self.client.session_transaction() as sess:
            sess["samlAttributes"] = {"whatever": ["USERNAME"]}

        self.assertRequestResponse(
            "/service/user",
            "USERNAME",
        )

    @pytest.mark.xfail(reason="need auth")
    def test_get_user_returns_username_from_name_id(self):
        with self.client.session_transaction() as sess:
            sess["samlNameId"] = "USERNAME"

        self.assertRequestResponse(
            "/service/user",
            "USERNAME",
        )

    @pytest.mark.xfail(reason="need auth")
    def test_get_user_no_username(self):
        self.assertRequestResponse(
            "/service/user",
            None,
        )
