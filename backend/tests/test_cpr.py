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
    def uuids(self, **overrides):
        UUID_OK = "12345678-9abc-def1-1111-111111111111"

        return {
            "SP_SERVICE_UUID": UUID_OK,
            "SP_SERVICE_AGREEMENT_UUID": UUID_OK,
            "SP_MUNICIPALITY_UUID": UUID_OK,
            "SP_SYSTEM_UUID": UUID_OK,
            **overrides,
        }

    def test_serviceplatformen_dummy_true(self):
        "test bad/missing values in config for Serviceplatformen "
        "are not considered in dummy mode"
        with util.override_app_config(
            ENV='production',
            DUMMY_MODE=True,
        ):
            self.assertTrue(serviceplatformen.check_config(self.app))

    def test_serviceplatformen_missing_path(self):
        with util.override_app_config(ENV='production', DUMMY_MODE=False,
                                      **self.uuids()):
            with self.assertRaisesRegex(
                ValueError,
                "Serviceplatformen certificate path must be configured: "
                "SP_CERTIFICATE_PATH"
            ):
                serviceplatformen.check_config(self.app)

    def test_serviceplatformen_empty_file(self):

        with tempfile.NamedTemporaryFile() as tf, util.override_app_config(
            ENV='production', DUMMY_MODE=False,
            SP_CERTIFICATE_PATH=tf.name,
            **self.uuids(),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Serviceplatformen certificate can not be empty: "
                "SP_CERTIFICATE_PATH"
            ):
                serviceplatformen.check_config(self.app)

    def test_serviceplatformen_invalid_values(self):
        with tempfile.NamedTemporaryFile() as tf, util.override_app_config(
            ENV='production', DUMMY_MODE=False,
            SP_CERTIFICATE_PATH=tf.name,
            **self.uuids(SP_SYSTEM_UUID="some-other-string-with-4dashes",
                         SP_SERVICE_UUID='asd'),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Serviceplatformen uuids must be valid: "
                "SP_SERVICE_UUID, SP_SYSTEM_UUID"
            ):
                serviceplatformen.check_config(self.app)

        with util.override_app_config(
            ENV='production',
            DUMMY_MODE=False,
            SP_CERTIFICATE_PATH=tf.name,
            **self.uuids(),
        ):
            with self.assertRaisesRegex(
                FileNotFoundError,
                "Serviceplatformen certificate not found: "
                "SP_CERTIFICATE_PATH"
            ):
                serviceplatformen.check_config(self.app)
