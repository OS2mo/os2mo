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
            lines = f.readlines()
        json_str = ''.join(lines)
        return json.loads(json_str)

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
        assert b'[]\n' == rv.data

    @requests_mock.mock()
    def test_list_organisations(self, mock):
        lora_response = self._jsonfile_to_dict('tests/mocking/lora/organisation/organisation/get_org_from_uuid.json')

        mock.get(self._get_lora_url('org_org_bvn'), json={'results': [['f58a99a5-a34f-4c6a-8fb2-118a2e25eacb']]})
        mock.get(self._get_lora_url('org_org_uuid'), json=lora_response)

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/list_organisations.json')
        actual_response = self._request('/o/')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for list_organisations')

    def _standard_mock_setup(self, mock):
        pass

    @requests_mock.mock()
    def test_full_hierarchy_no_treetype(self, mock):
        lora_org_response = self._jsonfile_to_dict('tests/mocking/lora/organisation/organisation/get_org_from_uuid.json')

        mock.get(self._get_lora_url('org_org_uuid'), json=lora_org_response)
        mock.get(self._get_lora_url('org_orgEnhed_tilhoerer'),
                 json=self._jsonfile_to_dict('tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_tilhoerer.json'))
        mock.get(self._get_lora_url('org_orgEnhed_uuidx3'),
                 json=self._jsonfile_to_dict('tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_uuidx3.json'))
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer1'), json={'results': [[]]})
        mock.get(self._get_lora_url('org_orgEnhed_overordnet_tilhoerer2'), json={'results': [[]]})

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/full-hierarchy_no_treetype.json')
        actual_response = self._request('/o/f58a99a5-a34f-4c6a-8fb2-118a2e25eacb/full-hierarchy?effective-date=&query=')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for full_hierarchy (no treetype)')

    @requests_mock.mock()
    def test_full_hierarchy_with_treetype(self, mock):
        lora_org_response = self._jsonfile_to_dict('tests/mocking/lora/organisation/organisation/get_org_from_uuid.json')

        mock.get(self._get_lora_url('org_org_uuid'), json=lora_org_response)
        mock.get(self._get_lora_url('org_orgEnhed_tilhoerer'),
                 json=self._jsonfile_to_dict('tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_tilhoerer.json'))
        mock.get(self._get_lora_url('org_orgEnhed_uuidx3'),
                 json=self._jsonfile_to_dict('tests/mocking/lora/organisation/organisationenhed/get_orgEnhed_from_uuidx3.json'))

        expected_response = self._jsonfile_to_dict('tests/mocking/mo/full-hierarchy_with_treetype.json')
        actual_response = self._request('/o/f58a99a5-a34f-4c6a-8fb2-118a2e25eacb/full-hierarchy?effective-date=&query=&treeType=treeType')

        self.assertEqual(actual_response, expected_response, 'JSON do not match for full_hierarchy (treetype=treetype)')

if __name__ == '__main__':
    unittest.main()
