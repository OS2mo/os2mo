import json
import unittest

import requests_mock

import mora.app as mora
from mora import lora
from tests.util import jsonfile_to_dict

class MoraTestCase(unittest.TestCase):
    def setUp(self):
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()
        self.lora_urls = jsonfile_to_dict('tests/mocking/lora/url_map.json')

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

    @unittest.expectedFailure
    @requests_mock.mock()
    def test_list_organisations(self, mock):
        self._standard_mock_setup(mock)

        mock.get(self._get_lora_url('org_org_bvn'), json={'results': [['f58a99a5-a34f-4c6a-8fb2-118a2e25eacb']]})

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/list_organisations.json')
        actual_response = self._request('/o/')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for list_organisations')

    @unittest.expectedFailure
    @requests_mock.mock()
    def test_full_hierarchy_treetype_is_null(self, mock):
        self._standard_mock_setup(mock)

        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer1'), json={'results': [[]]})
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer2'), json={'results': [[]]})

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/full-hierarchy_treetype_null.json')
        actual_response = self._request('/o/f58a99a5-a34f-4c6a-8fb2-118a2e25eacb/full-hierarchy?effective-date=&query=')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for full_hierarchy (no treetype)')

    @unittest.expectedFailure
    @requests_mock.mock()
    def test_full_hierarchy_treetype_is_treetype(self, mock):
        self._standard_mock_setup(mock)

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/full-hierarchy_treetype_treetype.json')
        actual_response = self._request(
            '/o/f58a99a5-a34f-4c6a-8fb2-118a2e25eacb/full-hierarchy?effective-date=&query=&treeType=treeType')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for full_hierarchy (treetype=treetype)')

    @unittest.expectedFailure
    @requests_mock.mock()
    def test_full_hierarchy_treetype_is_specific(self, mock):
        lora_org_response = self._jsonfile_to_dict(
            'tests/mocking/lora/organisation/organisation/get_org_from_uuid.json')
        mock.get(self._get_lora_url('org_org_uuid'), json=lora_org_response)
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer3'), json={
            'results': [
                [
                    '43b5dfc7-4d8c-494f-a954-d63379ffa1f3',
                    'da9491aa-123f-4218-9551-ff1fcefe4ddb'
                ]
            ]
        }
                 )
        lora_response = self._jsonfile_to_dict(
            'tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_uuidx2.json')
        mock.get(self._get_lora_url('org_orgEnhed_uuidx2'), json=lora_response)
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer1'), json={'results': [[]]})
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer2'), json={'results': [[]]})

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/full-hierarchy_treetype_specific.json')
        actual_response = self._request(
            '/o/f58a99a5-a34f-4c6a-8fb2-118a2e25eacb/full-hierarchy?effective-date=&query=&treeType=specific&orgUnitId=1ae72c47-b8f3-41ba-9c54-ed5c496c5bdd')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for full_hierarchy (treetype=specific)')

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
        mock.get(self._get_lora_url('klassifikation_klasse_uuidx2'), json=lora_klasse_response)

        expected_response = jsonfile_to_dict('tests/mocking/mo/list_classes.json')
        actual_response = self._request('/org-unit/type')

        self.assertEqual(actual_response, expected_response, 'Hurra')


class TestCreateOrgUnit(unittest.TestCase):

    def setUp(self):
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()
        self.lora_urls = jsonfile_to_dict('tests/mocking/lora/url_map.json')

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
        self.assertEqual(actual_response, expected_response, 'Error in creating org unit')
        self.assertEqual(r.status_code, 201, 'HTTP status code not 201')

    @requests_mock.mock()
    def test_create_organisation_unit_with_specific_end_date(self, mock):
        expected_response = {'uuid': '00000000-0000-0000-0000-000000000000'}
        frontend_req = jsonfile_to_dict(
            'tests/mocking/mo/create_org_unit_specific_enddate.json')
        mock.post(lora.LORA_URL + 'organisation/organisationenhed',
                  json=expected_response)
        mock.get('http://mox/organisation/organisationenhed?uuid=00000000-0000-0000-0000-000000000000',
                 json=jsonfile_to_dict('tests/mocking/lora/organisation/organisationenhed/get_org_unit_from_uuid.json'))
        mock.put('http://mox/organisation/organisationenhed/00000000-0000-0000-0000-000000000000',
                 json=expected_response)
        r = self.app.post('/o/' + frontend_req['org'] + '/org-unit',
                          data=json.dumps(frontend_req),
                          content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response, expected_response, 'Error in creating org unit')
        self.assertEqual(r.status_code, 201, 'HTTP status code not 201')


class TestRenameOrgUnit(unittest.TestCase):
    # TODO: move JSON requests/responses into tests/mocking (JSON below also used in test_create_org_unit.py)

    def setUp(self):
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()

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
        lora_response = {
            'results': [
                [
                    {
                        'registreringer': [
                            {
                                'tilstande': {
                                    'organisationenhedgyldighed': [
                                        {
                                            'virkning': {
                                                'from_included': True, 'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            },
                                            'gyldighed': 'Aktiv'
                                        }
                                    ]
                                },
                                'fratidspunkt': {
                                    'graenseindikator': True,
                                    'tidsstempeldatotid': '2017-06-02T12:57:21.367559+00:00'
                                },
                                'brugerref': '42c432e8-9c4a-11e6-9f62-873cf34a735f',
                                'attributter': {
                                    'organisationenhedegenskaber': [
                                        {
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            },
                                            'brugervendtnoegle': 'A6',
                                            'enhedsnavn': 'A6'
                                        }
                                    ]
                                },
                                'livscykluskode': 'Rettet',
                                'tiltidspunkt': {
                                    'tidsstempeldatotid': 'infinity'
                                },
                                'relationer': {
                                    'tilhoerer': [
                                        {
                                            'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            }
                                        }
                                    ],
                                    'adresser': [
                                        {
                                            'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            }
                                        },
                                    ],
                                    'enhedstype': [
                                        {
                                            'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            }
                                        }
                                    ],
                                    'overordnet': [
                                        {
                                            'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                                            'virkning': {
                                                'from_included': True,
                                                'from': '2017-05-07 22:00:00+00',
                                                'to': '2017-07-30 22:00:00+00',
                                                'to_included': False
                                            }
                                        }
                                    ]
                                }
                            }
                        ],
                        'id': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'
                    }
                ]
            ]
        }
        mock.get('http://mox/organisation/organisationenhed?uuid=65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
                 json=lora_response)
        mock.put('http://mox/organisation/organisationenhed/65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
                 json={'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'})
        r = self.app.post('/o/' + frontend_req['org'] + '/org-unit/' + frontend_req['uuid'] + '?rename=true',
                          data=json.dumps(frontend_req),
                          content_type='application/json')
        actual_response = json.loads(r.data.decode())
        self.assertEqual(actual_response, {'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5'}, 'Error in renaming org unit')
        self.assertEqual(r.status_code, 200, 'HTTP status code not 200')


if __name__ == '__main__':
    unittest.main()
