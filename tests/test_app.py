#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import unittest

import requests_mock

from mora import app
from mora import lora
from tests.util import jsonfile_to_dict


class TestSetup(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        self.lora_urls = jsonfile_to_dict('tests/mocking/lora/url_map.json')


class MoraTestCase(TestSetup):
    def _request(self, url):
        """
        Make request to the app, get a JSON response and convert this to a Python dictionary
        :param url: url to request in the app
        :return: dictionary representing the JSON response from the app
        """
        return json.loads(self.app.get(url).data.decode())

    def _get_lora_url(self, key):
        """
        Return the URL to call in LoRa for the given key
        :param key: the key used in the url_map.json file
        :return: URL in LoRa as a string
        """
        return lora.LORA_URL + self.lora_urls[key]

    def test_acl(self):
        rv = self.app.get('/acl/')
        self.assertEqual(b'[]\n', rv.data, 'Acl route should return empty list')

    def _standard_mock_setup(self, mock):
        lora_org_response = self._jsonfile_to_dict(
            'tests/mocking/lora/organisation/organisation/get_org_from_uuid.json')
        mock.get(self._get_lora_url('org_org_uuid'), json=lora_org_response)
        mock.get(self._get_lora_url('org_orgEnhed_tilhoerer'),
                 json=self._jsonfile_to_dict(
                     'tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_tilhoerer.json'))
        mock.get(self._get_lora_url('org_orgEnhed_uuidx3'),
                 json=self._jsonfile_to_dict(
                     'tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_uuidx3.json'))

    @requests_mock.mock()
    def test_list_classes(self, mock):
        lora_klasse_response = jsonfile_to_dict(
            'tests/mocking/lora/klassifikation/klasse/get_klasse_from_uuidx2.json')
        mock.get(self._get_lora_url('klassifikation_klasse_bvn'), json={
            'results': [
                [
                    'eb3dc9d3-297d-4c3d-9056-435d7696a8e9',
                    '14cf4675-e8c9-410f-aef4-abe3e4c1a9b7'
                ]
            ]
        }
                 )
        mock.get(self._get_lora_url('klassifikation_klasse_uuidx2'),
                 json=lora_klasse_response)

        expected_response = jsonfile_to_dict(
            'tests/mocking/mo/list_classes.json')
        actual_response = self._request('/org-unit/type')

        self.assertEqual(actual_response, expected_response, 'Hurra')


class TestCreateOrgUnit(TestSetup):
    @requests_mock.mock()
    def test_create_organisation_unit_with_end_date_infinity(self, mock):
        expected_response = {'uuid': '00000000-0000-0000-0000-000000000000'}
        frontend_req = jsonfile_to_dict('tests/mocking/mo/create_org_unit.json')
        mock.post(lora.LORA_URL + 'organisation/organisationenhed',
                  json=expected_response)
        r = self.app.post('/o/' + frontend_req['org'] + '/org-unit',
                          data=json.dumps(frontend_req),
                          content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response, expected_response,
                         'Error in creating org unit')
        self.assertEqual(r.status_code, 201, 'HTTP status code not 201')

    @requests_mock.mock()
    def test_create_organisation_unit_with_specific_end_date(self, mock):
        expected_response = {'uuid': '00000000-0000-0000-0000-000000000000'}
        frontend_req = jsonfile_to_dict(
            'tests/mocking/mo/create_org_unit_specific_enddate.json')
        mock.post(lora.LORA_URL + 'organisation/organisationenhed',
                  json=expected_response)
        mock.get(
            lora.LORA_URL + 'organisation/organisationenhed?uuid=00000000-0000-0000-0000-000000000000',
            json=jsonfile_to_dict(
                'tests/mocking/lora/organisation/organisationenhed/get_org_unit_from_uuid.json'))
        mock.put(
            lora.LORA_URL + 'organisation/organisationenhed/00000000-0000-0000-0000-000000000000',
            json=expected_response)
        r = self.app.post('/o/' + frontend_req['org'] + '/org-unit',
                          data=json.dumps(frontend_req),
                          content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response, expected_response,
                         'Error in creating org unit')
        self.assertEqual(r.status_code, 201, 'HTTP status code not 201')

# TODO: the tests below do not really tell us much...


class TestRenameOrgUnit(TestSetup):

    @requests_mock.mock()
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
            lora.LORA_URL + 'organisation/organisationenhed/65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
            json={'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'})
        r = self.app.post(
            '/o/' + frontend_req['org'] + '/org-unit/' + frontend_req[
                'uuid'] + '?rename=true',
            data=json.dumps(frontend_req),
            content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response,
                         {'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'},
                         'Error in renaming org unit')
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')


class TestInactivateOrgUnit(TestSetup):
    @requests_mock.mock()
    def test_should_respond_uuid_200_when_inactivating_org_unit(self, mock):
        mock.put(
            'http://mox/organisation/organisationenhed/00000000-0000-0000-0000-000000000000',
            json={'uuid': '00000000-0000-0000-0000-000000000000'})
        r = self.app.delete(
            '/o/00000000-0000-0000-0000-000000000000/org-unit/00000000-0000-0000-0000-000000000000?endDate=01-01-2010')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response,
                         {'uuid': '00000000-0000-0000-0000-000000000000'},
                         'Error when inactivating org unit')
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')


class TestMoveOrgUnit(TestSetup):
    @requests_mock.mock()
    def test_should_respond_uuid_200_when_moving_org_unit(self, mock):
        frontend_req = {
            "moveDate": "01-01-2010",
            "newParentOrgUnitUUID": "00000000-0000-0000-0000-000000000000"}
        mock.put(
            'http://mox/organisation/organisationenhed/00000000-0000-0000-0000-000000000000',
            json={'uuid': '00000000-0000-0000-0000-000000000000'})
        r = self.app.post(
            '/o/00000000-0000-0000-0000-000000000000/org-unit/00000000-0000-0000-0000-000000000000/actions/move',
            data=json.dumps(frontend_req),
            content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response,
                         {'uuid': '00000000-0000-0000-0000-000000000000'},
                         'Error when moving org unit')
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')


if __name__ == '__main__':
    unittest.main()
