# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from . import util
from unittest.mock import patch


async def async_helper1():
    return []


async def async_helper2():
    return [{}, {}]


class Tests(util.TestCase):
    maxDiff = None

    @patch('mora.service.org.get_valid_organisations', new=async_helper1)
    def test_no_orgs_in_mo(self):
        r = self.request('/service/o/')
        self.assertEqual({
            'error': True,
            'error_key': 'E_ORG_UNCONFIGURED',
            'status': 400,
            'description': 'Organisation has not been configured'
        }, r.json)

    @patch('mora.service.org.get_valid_organisations', new=async_helper2)
    def test_more_than_one_org_in_mo(self):
        r = self.request('/service/o/')
        self.assertEqual({
            'error': True,
            'count': 2,
            'error_key': 'E_ORG_TOO_MANY',
            'status': 400,
            'description': 'Too many organisations in lora, max one allowed'
        }, r.json)
