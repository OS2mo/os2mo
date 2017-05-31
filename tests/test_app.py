import unittest
import mora.app as mora
import requests_mock
import json
from pprint import pprint
from mora import lora


class MoraTestCase(unittest.TestCase):
    def setUp(self):
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()
        self.lora_urls = self._jsonfile_to_dict('tests/mocking/lora/url_map.json')

    def tearDown(self):
        pass

    # Careful here - test code must not be "complicated"...
    def _jsonfile_to_dict(self, path):
        """
        Reads JSON from resources folder and converts to Python dictionary
        :param path: path to json resource 
        :return: dictionary corresponding to the resource JSON
        """
        with open(path) as f:
            return json.load(f)

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
        lora_klasse_response = self._jsonfile_to_dict(
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

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/list_classes.json')
        actual_response = self._request('/org-unit/type')

        self.assertEqual(actual_response, expected_response, 'Hurra')

    @requests_mock.mock()
    def test_create_organisation_unit(self, mock):
        frontend_req = self._jsonfile_to_dict('tests/mocking/mo/create_org_unit.json')
        mock.post(lora.LORA_URL + 'organisation/organisationenhed',
                  json={'uuid': '00000000-0000-0000-0000-000000000000'})
        r = self.app.post('/o/' + frontend_req['org'] + '/org-unit',
                          data=json.dumps(frontend_req),
                          content_type='application/json')
        # TODO: check this - should response really be a string and not JSON?
        self.assertEqual(r.data.decode(), '00000000-0000-0000-0000-000000000000', 'Error in creating org unit')
        self.assertEqual(r.status_code, 201, 'HTTP status code not 201')


if __name__ == '__main__':
    unittest.main()
