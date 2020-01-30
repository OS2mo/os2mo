# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from unittest.mock import patch

from mora import exceptions
from mora.service.address_handler import email
from .. import util


@patch('mora.service.facet.get_one_class', new=lambda x, y: {'uuid': y})
class EmailAddressHandlerTests(util.TestCase):
    handler = email.EmailAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = 'mail@mail.dk'

    def test_from_effect(self):
        # Arrange
        value = 'mail@mail.dk'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:mailto:{}'.format(value)
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_from_request(self):
        # Arrange
        value = 'mail@mail.dk'

        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_get_mo_address(self):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = {
            'href': 'mailto:mail@mail.dk',
            'name': 'mail@mail.dk',
            'value': 'mail@mail.dk',
            'visibility': {'uuid': 'dd5699af-b233-44ef-9107-7a37016b2ed1'}
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'mail@mail.dk'
        address_handler = self.handler(value, None)

        expected = {
            'objekttype': 'EMAIL',
            'urn': 'urn:mailto:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        value = 'asdasd'  # Not a valid email address

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            'test@test.com',
            'test+hest@test.com',
            't.e.s.t@test.com'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid email address

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)
