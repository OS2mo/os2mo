#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import unittest

from . import util


class TestSetup(util.TestCase):
    def setUp(self):
        self.lora_urls = util.get_mock_data('lora/url_map.json')

        super().setUp()


class MoraTestCase(TestSetup):
    def _request(self, url):
        """Make request to the app, get a JSON response and convert this to a
        Python dictionary

        :param url: url to request in the app
        :return: dictionary representing the JSON response from the app
        """
        return json.loads(self.client.get(url).data.decode())

    def _get_lora_url(self, key):
        """
        Return the URL to call in LoRa for the given key
        :param key: the key used in the url_map.json file
        :return: URL in LoRa as a string
        """
        return self.lora_url + self.lora_urls[key]

    def test_acl(self):
        rv = self.client.get('/acl/')
        self.assertEqual(b'[]\n', rv.data,
                         'Acl route should return empty list')

    @util.mock()
    def test_list_classes(self, mock):
        lora_klasse_response = util.get_mock_data(
            'lora/klassifikation/klasse/get_klasse_from_uuidx2.json',
        )
        mock.get(self._get_lora_url('klassifikation_klasse_bvn'), json={
            'results': [
                [
                    'eb3dc9d3-297d-4c3d-9056-435d7696a8e9',
                    '14cf4675-e8c9-410f-aef4-abe3e4c1a9b7'
                ]
            ]
        })
        mock.get(self._get_lora_url('klassifikation_klasse_uuidx2'),
                 json=lora_klasse_response)

        expected_response = util.get_mock_data('mo/list_classes.json')
        actual_response = self._request('/org-unit/type')

        self.assertEqual(actual_response, expected_response, 'Hurra')

    @util.mock()
    def test_invalid_operations(self, mock):
        # we should do network I/O in the test, and 'empty' mocking
        # verifies that

        self.assertRequestResponse(
            '/o/00000000-0000-0000-0000-000000000000'
            '/org-unit/00000000-0000-0000-0000-000000000000/?query=fail',
            {
                'message': 'unitid and query cannot both be set!',
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/o/00000000-0000-0000-0000-000000000000'
            '/org-unit/00000000-0000-0000-0000-000000000000/'
            'role-types/fail/',
            {
                'message': "unsupported role 'fail'",
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/o/00000000-0000-0000-0000-000000000000'
            '/full-hierarchy?query=fail',
            {
                'message': 'sub-tree searching is unsupported!',
                'status': 400,
            },
            status_code=400,
        )


class TestRenameAndRetypeOrgUnit(TestSetup):
    @util.mock()
    def test_should_rename_org_unit_correctly(self, mock):
        frontend_req = {
            'name': 'A6om',
            'user-key': 'A6',
            'parent-object': {
                'name': 'Øvrige Enheder',
                'user-key': 'ØVRIGE',
                'parent-object': {
                    'name': 'Aarhus Kommune',
                    'user-key': 'ÅRHUS',
                    'parent-object': None,
                    'valid-to': 'infinity',
                    'activeName': 'Aarhus Kommune',
                    'valid-from': '2015-12-31 23:00:00+00',
                    'uuid': '7454a573-5dab-4c2f-baf2-89f273286dec',
                    'hasChildren': True,
                    'org': '59141156-ed0b-457c-9535-884447c5220b',
                    'parent': None},
                'valid-to': 'infinity',
                'activeName': 'Øvrige Enheder',
                'valid-from': '2015-12-31 23:00:00+00',
                'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                'hasChildren': True,
                'org': '59141156-ed0b-457c-9535-884447c5220b',
                'parent': '7454a573-5dab-4c2f-baf2-89f273286dec'},
            'valid-to': '27-07-2026',
            'activeName': 'A6',
            'valid-from': '25-07-2025',
            'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
            'hasChildren': False,
            'org': '59141156-ed0b-457c-9535-884447c5220b',
            'parent': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc'
        }
        mock.put(
            'http://mox/organisation/organisationenhed/'
            '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
            json={'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'})
        r = self.client.post(
            '/o/' + frontend_req['org'] + '/org-unit/' + frontend_req[
                'uuid'] + '?rename=true',
            data=json.dumps(frontend_req),
            content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response,
                         {'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'},
                         'Error in renaming org unit')
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')

    @util.mock()
    def test_should_retype_org_unit_correctly(self, mock):
        frontend_req = util.get_mock_data('mo/retype_org_unit.json')
        mock.put(
            'http://mox/organisation/organisationenhed/'
            '383e5dfd-e41c-4a61-9cdc-f8c5ea9b1cbe',
            json={'uuid': '383e5dfd-e41c-4a61-9cdc-f8c5ea9b1cbe'})
        r = self.client.post(
            '/o/' + frontend_req['org'] + '/org-unit/' + frontend_req[
                'uuid'], data=json.dumps(frontend_req),
            content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual({'uuid': '383e5dfd-e41c-4a61-9cdc-f8c5ea9b1cbe'},
                         actual_response)
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')


if __name__ == '__main__':
    unittest.main()
