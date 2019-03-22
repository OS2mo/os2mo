#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest.mock import patch

from mora.service.address_handler import (
    dar, ean, email, phone, pnumber, text, www)
from mora import exceptions
from . import util


@util.mock('dawa-addresses.json')
class DarAddressHandlerTests(util.TestCase):
    handler = dar.DARAddressHandler

    def test_from_effect(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:dar:{}'.format(value)
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_from_request(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_get_mo_address(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'
        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        expected = {
            'href': 'https://www.openstreetmap.org/?mlon=12.57924839'
                    '&mlat=55.68113676&zoom=16',
            'name': 'Pilestræde 43, 3., 1112 København K',
            'value': '0a3f50a0-23c9-32b8-e044-0003ba298018'
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'DAR',
            'urn': 'urn:dar:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_validation_fails_on_invalid_value(self, mock):
        # Arrange
        value = '1234'  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_fails_on_unknown_uuid(self, mock):
        # Arrange
        value = 'e30645d3-2c2b-4b9f-9b7a-3b7fc0b4b80d'  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_uuid(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        # Act & Assert
        # Assert that no exception is raised
        self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self, mock):
        # Arrange
        valid_values = [
            '0a3f50a0-23c9-32b8-e044-0003ba298018'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self, mock):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid DAR UUID

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)

    def test_failed_lookup_from_request(self, mock):
        """Ensure that failed request lookups are handled appropriately"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'

        # Act & Assert
        with self.assertRaisesRegex(exceptions.HTTPException, "DAR Address"):
            request = {
                'value': value
            }
            self.handler.from_request(request)

    def test_failed_lookup_from_effect(self, mock):
        """Ensure that failed effect lookups are handled appropriately"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'

        expected = {
            'href': None,
            'name': 'Ukendt',
            'value': '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'
        }

        # Act
        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:dar:{}'.format(value)
                }]
            }
        }
        address_handler = self.handler.from_effect(effect)

        self.assertEqual(expected,
                         address_handler.get_mo_address_and_properties())


class EANAddressHandlerTests(util.TestCase):
    handler = ean.EANAddressHandler

    def test_from_effect(self):
        # Arrange
        value = '1234567890123'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:magenta.dk:ean:{}'.format(value)
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
        value = '1234567890123'

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
        value = '1234567890123'
        address_handler = self.handler(value)

        expected = {
            'href': None,
            'name': value,
            'value': value
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = '1234567890123'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'EAN',
            'urn': 'urn:magenta.dk:ean:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = '1234567890123'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        value = '1234'  # Not a valid EAN

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            "1234123412341"
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid EAN

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)


class EmailAddressHandlerTests(util.TestCase):
    handler = email.EmailAddressHandler

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
        value = 'mail@mail.dk'
        address_handler = self.handler(value)

        expected = {
            'href': 'mailto:mail@mail.dk',
            'name': 'mail@mail.dk',
            'value': 'mail@mail.dk'
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'mail@mail.dk'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'EMAIL',
            'urn': 'urn:mailto:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = 'mail@mail.dk'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

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


class PhoneAddressHandlerTests(util.TestCase):
    handler = phone.PhoneAddressHandler

    def test_from_effect(self):
        # Arrange
        visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
        value = '+4512345678'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:magenta.dk:telefon:+4512345678'
                }],
                'opgaver': [{
                    'objekttype': 'synlighed',
                    'uuid': visibility
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    def test_from_request(self):
        # Arrange
        visibility = '0261fdd3-4aa3-4c9b-9542-8163a1184738'
        request = {
            'value': '12345678',
            'visibility': {
                'uuid': visibility
            }
        }
        address_handler = self.handler.from_request(request)

        expected_value = '+4512345678'

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(expected_value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    def test_get_mo_address(self):
        # Arrange
        value = '12345678'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = {
            'href': 'tel:+4512345678',
            'name': '+4512345678',
            'value': '12345678',
            'visibility': {
                'uuid': visibility
            }
        }

        # Act
        with patch(
            'mora.service.address_handler.phone.facet.get_one_class',
            new=lambda x, y: {'uuid': y}
        ):
            actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = '12345678'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = {
            'objekttype': 'PHONE',
            'urn': 'urn:magenta.dk:telefon:+4512345678'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = '12345678'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = [{
            'objekttype': 'synlighed',
            'uuid': 'd99b500c-34b4-4771-9381-5c989eede969'
        }]

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            # Not a valid phone number
            self.handler.validate_value('asdasd')

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            '+4520931217'
            '12341234'
            '123'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid phone number

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)


class PNumberAddressHandlerTests(util.TestCase):
    handler = pnumber.PNumberAddressHandler

    def test_from_effect(self):
        # Arrange
        value = '1234567890'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:dk:cvr:produktionsenhed:{}'.format(value)
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
        value = '1234567890'

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
        value = '1234567890'
        address_handler = self.handler(value)

        expected = {
            'href': None,
            'name': value,
            'value': value
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = '1234567890'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'PNUMBER',
            'urn': 'urn:dk:cvr:produktionsenhed:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = '1234567890'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        value = '1234'  # Not a valid P-number

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            '1234123412'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid P-number

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)


class TextAddressHandlerTests(util.TestCase):
    handler = text.TextAddressHandler

    def test_from_effect(self):
        # Arrange
        value = 'Test text whatever'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:text:%54est%20text%20whatever'
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
        value = 'Test text whatever'

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
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = {
            'href': None,
            'name': value,
            'value': value
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'TEXT',
            'urn': 'urn:text:%54est%20text%20whatever'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)


class WWWAddressHandlerTests(util.TestCase):
    handler = www.WWWAddressHandler

    def test_from_effect(self):
        # Arrange
        value = 'http://www.test.org/'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:magenta.dk:www:{}'.format(value)
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
        value = 'http://www.test.org/'

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
        value = 'http://www.test.org/'
        address_handler = self.handler(value)

        expected = {
            'href': None,
            'name': value,
            'value': value
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'http://www.test.org/'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'WWW',
            'urn': 'urn:magenta.dk:www:http://www.test.org/'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = 'http://www.test.org/'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_validation_fails_on_invalid_value(self):
        # Arrange
        value = '@$@#$@#$'  # Not a valid URL

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            'http://www.test.com',
            'https://www.test.com',
            'http://subdomain.hej.com/welcome/to/test.html',
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid URL

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)
