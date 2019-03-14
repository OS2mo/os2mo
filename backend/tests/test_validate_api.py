#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mock import patch, MagicMock

from mora import util as mora_util
from . import util


class TestValidateAPI(util.TestCase):

    @patch('mora.service.validate.validator.is_date_range_in_org_unit_range')
    def test_candidate_org_unit(self, mock):
        org_unit_uuid = "be0df80c-7eed-4a2e-a682-e36be4e4877e"
        from_date = "2000-01-01"

        payload = {
            "org_unit": {
                "uuid": org_unit_uuid
            },
            "validity": {
                "from": from_date,
                "to": None
            }
        }

        self.client.post('/service/validate/org-unit/', json=payload)

        mock.assert_called_with(
            org_unit_uuid,
            mora_util.parsedatetime(from_date),
            mora_util.POSITIVE_INFINITY
        )

    @patch('mora.service.validate.validator.is_date_range_in_employee_range')
    def test_candidate_employee(self, mock):
        from_date = "2000-01-01"

        person = {
            "uuid": "be0df80c-7eed-4a2e-a682-e36be4e4877e"
        }
        payload = {
            "person": person,
            "validity": {
                "from": from_date,
                "to": None
            }
        }

        self.client.post('/service/validate/employee/', json=payload)

        mock.assert_called_with(
            person,
            mora_util.parsedatetime(from_date),
            mora_util.POSITIVE_INFINITY
        )

    @patch('mora.service.validate.validator.'
           'does_employee_with_cpr_already_exist')
    def test_cpr(self, mock):
        from_date = "2000-01-01"
        cpr_no = "1234567890"

        org_uuid = "52e8d1ff-6fe0-4e8a-a19c-8bd8e1154b3b"
        payload = {
            "cpr_no": cpr_no,
            "org": {
                "uuid": org_uuid
            },
            "validity": {
                "from": from_date,
                "to": None
            }
        }

        self.client.post('/service/validate/cpr/', json=payload)

        mock.assert_called_with(
            cpr_no,
            mora_util.parsedatetime(from_date),
            mora_util.POSITIVE_INFINITY,
            org_uuid
        )

    @patch('mora.service.validate.validator.'
           'does_employee_have_active_engagement')
    def test_employee_engagements(self, mock):
        person_uuid = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
        from_date = "2000-01-01"

        payload = {
            "person": {
                "uuid": person_uuid
            },
            "validity": {
                "from": from_date,
                "to": None
            }
        }

        self.client.post('/service/validate/active-engagements/', json=payload)

        mock.assert_called_with(
            person_uuid,
            mora_util.parsedatetime(from_date),
            mora_util.POSITIVE_INFINITY,
        )

    @patch('mora.service.validate.validator.'
           'does_employee_have_existing_association')
    def test_existing_associations(self, mock):
        person_uuid = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
        org_unit_uuid = "f4f28810-cdd9-4ff5-821e-427378ab4bf7"
        from_date = "2000-01-01"

        payload = {
            "person": {
                "uuid": person_uuid
            },
            "org_unit": {
                "uuid": org_unit_uuid
            },
            "validity": {
                "from": from_date,
                "to": None
            }
        }

        self.client.post('/service/validate/existing-associations/',
                         json=payload)

        mock.assert_called_with(
            person_uuid,
            org_unit_uuid,
            mora_util.parsedatetime(from_date),
            mora_util.POSITIVE_INFINITY
        )

    @patch('mora.service.validate.validator.'
           'is_candidate_parent_valid')
    def test_parent_org_unit(self, mock):
        from_date = "2000-01-01"
        org_unit_uuid = "f4f28810-cdd9-4ff5-821e-427378ab4bf7"
        parent_uuid = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"

        payload = {
            "org_unit": {
                "uuid": org_unit_uuid
            },
            "parent": {
                "uuid": parent_uuid
            },
            "validity": {
                "from": from_date,
            }
        }

        self.client.post('/service/validate/candidate-parent-org-unit/',
                         json=payload)

        mock.assert_called_with(
            org_unit_uuid,
            parent_uuid,
            mora_util.parsedatetime(from_date)
        )

    @patch('mora.service.address_handler.base.get_handler_for_scope')
    @patch('mora.service.facet.get_one_class')
    def test_address(self, get_one_class, get_handler_for_scope):
        value = "12341234"
        scope = 'SCOPE'

        payload = {
            "address_type": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "value": value
        }

        get_one_class.return_value = {
            'scope': scope
        }

        get_handler_for_scope.return_value = handler = MagicMock()

        self.client.post('/service/validate/address/', json=payload)

        get_handler_for_scope.assert_called_with(scope)
        handler.validate_value.assert_called_with(value)
