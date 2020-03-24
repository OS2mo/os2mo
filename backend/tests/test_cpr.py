# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun

from . import util
from mora import util as mora_util
from mora.integrations import serviceplatformen
import tempfile


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock()
class Tests(util.TestCase):
    maxDiff = None

    def test_cpr_lookup_dummy_mode_true(self, m):
        with self.subTest('found'):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=0101501234',
                {
                    'name': 'Merle Mortensen',
                    'cpr_no': "0101501234"
                })

        with self.subTest('too early'):
            self.assertEqual(mora_util.get_cpr_birthdate(2004936541).year,
                             1893)

            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=2004936541',
                {
                    'cpr': '2004936541',
                    'description': 'No person found for given CPR number.',
                    'error': True,
                    'error_key': 'V_NO_PERSON_FOR_CPR',
                    'status': 404,
                },
                status_code=404,
            )

        with self.subTest('too late'):
            self.assertEqual(mora_util.get_cpr_birthdate(2004256543).year,
                             2025)

            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=2004256543',
                {
                    'cpr': '2004256543',
                    'description': 'No person found for given CPR number.',
                    'error': True,
                    'error_key': 'V_NO_PERSON_FOR_CPR',
                    'status': 404,
                },
                status_code=404,
            )

        with self.subTest('not a cpr number'):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=1337',
                {
                    'cpr': '1337',
                    'error_key': 'V_CPR_NOT_VALID',
                    'description': 'Not a valid CPR number.',
                    'error': True,
                    'status': 400,
                },
                status_code=400,
            )

    def test_cpr_lookup_raises_on_wrong_length(self, m):
        # Arrange

        # Act
        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234/',
            {
                'cpr': '1234/',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=111111111',
            {
                'cpr': '111111111',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234567890123',
            {
                'cpr': '1234567890123',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=2222222222',
            {
                'cpr': '2222222222',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )


class TestConfig(util.TestCase):
    def _sp_config(self, **overrides):
        UUID_OK = "12345678-9abc-def1-1111-111111111111"

        return {
            "service_platformen": {
                "uuid": UUID_OK,
                "agreement_uuid": UUID_OK,
                "municipality_uuid": UUID_OK,
                "system_uuid": UUID_OK,
                **overrides,
            }
        }

    def test_serviceplatformen_dummy_true(self):
        "test bad/missing values in config for Serviceplatformen "
        "are not considered in dummy mode"
        with util.override_app_config(ENV='production'):
            with util.override_config({"dummy_mode": True}):
                self.assertTrue(serviceplatformen.check_config(self.app))

    def test_serviceplatformen_missing_path(self):
        with util.override_app_config(ENV='production'):
            with util.override_config({
                "dummy_mode": False, **self._sp_config()}
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "Serviceplatformen certificate path must be configured"
                ):
                    serviceplatformen.check_config(self.app)

    def test_serviceplatformen_empty_file(self):
        with tempfile.NamedTemporaryFile() as tf:
            with util.override_app_config(ENV='production'):
                with util.override_config({
                    "dummy_mode": False,
                    **self._sp_config(certificate_path=tf.name)
                }):
                    with self.assertRaisesRegex(
                        ValueError,
                        "Serviceplatformen certificate can not be empty"
                    ):
                        serviceplatformen.check_config(self.app)

    def test_serviceplatformen_invalid_values(self):
        with tempfile.NamedTemporaryFile() as tf:
            with util.override_app_config(ENV='production'):
                with util.override_config({
                    "dummy_mode": False,
                    **self._sp_config(
                        system_uuid="some-other-string-with-4dashes",
                        uuid='asd'
                    )
                }):
                    with self.assertRaisesRegex(
                        ValueError,
                        "Serviceplatformen uuids must be valid: "
                        "uuid, system_uuid"
                    ):
                        serviceplatformen.check_config(self.app)

        # the temporary file has now been deleted by tempfile cm
        # but name still exists
        with util.override_app_config(ENV='production'):
            with util.override_config({
                "dummy_mode": False,
                **self._sp_config(certificate_path=tf.name)
            }):
                with self.assertRaisesRegex(
                    FileNotFoundError,
                    "Serviceplatformen certificate not found"
                ):
                    serviceplatformen.check_config(self.app)
