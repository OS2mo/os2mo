#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .. import util


class AddressHandlerTestCase(util.TestCase):
    handler = None
    value = None
    visibility = None

    def test_get_lora_properties(self, *args):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = [{
            'objekttype': 'synlighed',
            'uuid': self.visibility
        }]

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)
