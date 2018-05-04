#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora import exceptions
from mora import util as mora_util
from mora import validator
from tests import util


class TestValidator(util.LoRATestCase):

    def test_is_date_range_in_org_unit_valid_raises_outside_range(self):
        """Assert that a validation error is raised when the range exceeds
        org unit range """

        # Arrange
        self.load_sample_structures()
        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'  # Hum
        valid_from = mora_util.parsedatetime("1980-01-01")
        valid_to = mora_util.parsedatetime("2040-01-01")

        # Act & Assert
        with self.assertRaises(exceptions.ValidationError):
            validator.is_date_range_in_org_unit_range(org_unit_uuid,
                                                      valid_from, valid_to)

    def test_is_date_range_in_org_unit_valid_inside_range(self):
        """Assert that a validation error is not raised when the range is
        inside org unit range"""

        # Arrange
        self.load_sample_structures()
        org_unit_uuid = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'  # Hum
        valid_from = mora_util.parsedatetime("2020-01-01")
        valid_to = mora_util.parsedatetime("2040-01-01")

        # Act & Assert
        # Should be callable without raising exception
        validator.is_date_range_in_org_unit_range(org_unit_uuid,
                                                  valid_from, valid_to)

    def test_is_date_range_in_employee_valid_raises_outside_range(self):
        """Assert that a validation error is raised when the range exceeds
        employee range """

        # Arrange
        self.load_sample_structures()
        employee_uuid = '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'  # Anders And
        valid_from = mora_util.parsedatetime("1910-01-01")
        valid_to = mora_util.parsedatetime("2040-01-01")

        # Act & Assert
        with self.assertRaises(exceptions.ValidationError):
            validator.is_date_range_in_employee_range(employee_uuid,
                                                      valid_from, valid_to)

    def test_is_date_range_in_employee_valid_inside_range(self):
        """Assert that a validation error is not raised when the range is
        inside employee range"""

        # Arrange
        self.load_sample_structures()
        employee_uuid = '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'  # Anders And
        valid_from = mora_util.parsedatetime("2020-01-01")
        valid_to = mora_util.parsedatetime("2040-01-01")

        # Act & Assert
        # Should be callable without raising exception
        validator.is_date_range_in_employee_range(employee_uuid,
                                                  valid_from, valid_to)
