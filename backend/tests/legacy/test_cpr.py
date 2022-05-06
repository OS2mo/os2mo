# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import tempfile

import freezegun
import tests.legacy.cases

from . import util
from mora import util as mora_util
from mora.config import Settings
from mora.integrations import serviceplatformen


@freezegun.freeze_time("2017-01-01", tz_offset=1)
@util.mock(real_http=True)
class AsyncTests(tests.legacy.cases.AsyncTestCase):
    maxDiff = None

    async def test_cpr_lookup_dummy_mode_true(self, m):
        with self.subTest("found"):
            await self.assertRequestResponse(
                "/service/e/cpr_lookup/?q=0101501234",
                {"name": "Merle Mortensen", "cpr_no": "0101501234"},
            )

        with self.subTest("too early"):
            self.assertEqual(mora_util.get_cpr_birthdate(2004936541).year, 1893)

            await self.assertRequestResponse(
                "/service/e/cpr_lookup/?q=2004936541",
                {
                    "cpr": "2004936541",
                    "description": "No person found for given CPR number.",
                    "error": True,
                    "error_key": "V_NO_PERSON_FOR_CPR",
                    "status": 404,
                },
                status_code=404,
            )

        with self.subTest("too late"):
            self.assertEqual(mora_util.get_cpr_birthdate(2004256543).year, 2025)

            await self.assertRequestResponse(
                "/service/e/cpr_lookup/?q=2004256543",
                {
                    "cpr": "2004256543",
                    "description": "No person found for given CPR number.",
                    "error": True,
                    "error_key": "V_NO_PERSON_FOR_CPR",
                    "status": 404,
                },
                status_code=404,
            )

        with self.subTest("not a cpr number"):
            await self.assertRequestResponse(
                "/service/e/cpr_lookup/?q=1337",
                {
                    "cpr": "1337",
                    "error_key": "V_CPR_NOT_VALID",
                    "description": "Not a valid CPR number.",
                    "error": True,
                    "status": 400,
                },
                status_code=400,
            )

    async def test_cpr_lookup_raises_on_wrong_length(self, m):
        # Arrange

        # Act
        await self.assertRequestResponse(
            "/service/e/cpr_lookup/?q=1234/",
            {
                "cpr": "1234/",
                "error_key": "V_CPR_NOT_VALID",
                "description": "Not a valid CPR number.",
                "error": True,
                "status": 400,
            },
            status_code=400,
        )

        await self.assertRequestResponse(
            "/service/e/cpr_lookup/?q=111111111",
            {
                "cpr": "111111111",
                "error_key": "V_CPR_NOT_VALID",
                "description": "Not a valid CPR number.",
                "error": True,
                "status": 400,
            },
            status_code=400,
        )

        await self.assertRequestResponse(
            "/service/e/cpr_lookup/?q=1234567890123",
            {
                "cpr": "1234567890123",
                "error_key": "V_CPR_NOT_VALID",
                "description": "Not a valid CPR number.",
                "error": True,
                "status": 400,
            },
            status_code=400,
        )

        await self.assertRequestResponse(
            "/service/e/cpr_lookup/?q=2222222222",
            {
                "cpr": "2222222222",
                "error_key": "V_CPR_NOT_VALID",
                "description": "Not a valid CPR number.",
                "error": True,
                "status": 400,
            },
            status_code=400,
        )

    async def test_birthdate_validation_disabled(self, m):
        """Validation of CPR birthdate can be disabled by a feature flag"""
        with util.override_config(Settings(cpr_validate_birthdate=False)):
            await self.assertRequestResponse(
                "/service/e/cpr_lookup/?q=0121501234",
                {"name": "Naja Hansen", "cpr_no": "0121501234"},
            )


class TestConfig(tests.legacy.cases.TestCase):
    def _sp_config(self, **overrides):
        UUID_OK = "12345678-9abc-def1-1111-111111111111"

        return {
            "sp_service_uuid": UUID_OK,
            "sp_agreement_uuid": UUID_OK,
            "sp_municipality_uuid": UUID_OK,
            "sp_system_uuid": UUID_OK,
            **overrides,
        }

    def test_serviceplatformen_dummy_true(self):
        "test bad/missing values in config for Serviceplatformen"
        "are not considered in dummy mode"
        with util.override_config(Settings(environment="production", dummy_mode=True)):
            self.assertTrue(serviceplatformen.check_config())

    def test_serviceplatformen_missing_path(self):
        with util.override_config(
            Settings(environment="production", dummy_mode=False, **self._sp_config())
        ):
            with self.assertRaisesRegex(
                ValueError, "Serviceplatformen certificate path must be configured"
            ):
                serviceplatformen.check_config()

    def test_serviceplatformen_empty_file(self):
        with tempfile.NamedTemporaryFile() as tf:
            with util.override_config(
                Settings(
                    environment="production",
                    dummy_mode=False,
                    **self._sp_config(sp_certificate_path=tf.name)
                )
            ):
                with self.assertRaisesRegex(
                    ValueError, "Serviceplatformen certificate can not be empty"
                ):
                    serviceplatformen.check_config()
