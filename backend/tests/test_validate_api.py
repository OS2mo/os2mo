#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mock import patch

from . import util


class TestValidateAPI(util.TestCase):

    @patch('mora.service.validate.validator.is_date_range_in_org_unit_range')
    def test_candidate_org_unit(self, mock):
        payload = {
            "org_unit": {
                "uuid": "be0df80c-7eed-4a2e-a682-e36be4e4877e"
            },
            "validity": {
                "from": "2000-01-01",
                "to": None
            }
        }

        self.client.post('/validate/org-unit/', json=payload)

        mock.assert_called_once()

    @patch('mora.service.validate.validator.is_date_range_in_employee_range')
    def test_candidate_employee(self, mock):
        payload = {
            "person": {
                "uuid": "be0df80c-7eed-4a2e-a682-e36be4e4877e"
            },
            "validity": {
                "from": "2000-01-01",
                "to": None
            }
        }

        self.client.post('/validate/employee/', json=payload)

        mock.assert_called_once()

    @patch('mora.service.validate.validator.'
           'does_employee_with_cpr_already_exist')
    def test_cpr(self, mock):
        payload = {
            "cpr_no": "123456789",
            "org": {
                "uuid": "52e8d1ff-6fe0-4e8a-a19c-8bd8e1154b3b"
            },
            "validity": {
                "from": "2000-01-01",
                "to": None
            }
        }

        self.client.post('/validate/cpr/', json=payload)

        mock.assert_called_once()

    @patch('mora.service.validate.validator.'
           'does_employee_have_active_engagement')
    def test_employee_engagements(self, mock):
        payload = {
            "person": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "validity": {
                "from": "2000-01-01",
                "to": None
            }
        }

        self.client.post('/validate/active-engagements/', json=payload)

        mock.assert_called_once()

    @patch('mora.service.validate.validator.'
           'does_employee_have_existing_association')
    def test_existing_associations(self, mock):
        payload = {
            "person": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "org_unit": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "validity": {
                "from": "2000-01-01",
                "to": None
            }
        }

        self.client.post('/validate/existing-associations/', json=payload)

        mock.assert_called_once()

    @patch('mora.service.validate.validator.'
           'is_candidate_parent_valid')
    def test_parent_org_unit(self, mock):
        payload = {
            "org_unit": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "parent": {
                "uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
            },
            "validity": {
                "from": "2000-01-01",
            }
        }

        self.client.post('/validate/candidate-parent-org-unit/', json=payload)

        mock.assert_called_once()
