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

    def _request_to_dict(self, url):
        """
        Make request to the app, get a JSON response and convert this to a Python dictionary
        :param url: url to request in the app
        :return: dictionary representing the JSON response from the app
        """
        return json.loads(self.app.get(url).data.decode())

    def test_acl(self):
        rv = self.app.get('/acl/')
        assert b'[]\n' == rv.data

    @requests_mock.mock()
    def test_list_organisations(self, mock):
        lora_response = self._jsonfile_to_dict('tests/mocking/lora/lora_response_get_organisation_from_uuid.json')
        mock.get(lora.LORA_URL + 'organisation/organisation?bvn=%',
                 json={'results': [['f58a99a5-a34f-4c6a-8fb2-118a2e25eacb']]})
        mock.get(lora.LORA_URL + 'organisation/organisation?uuid=f58a99a5-a34f-4c6a-8fb2-118a2e25eacb',
                 json=lora_response)

        expected_response = self._jsonfile_to_dict('tests/mocking/mo_response_list_organisations.json')
        actual_response = json.loads(self.app.get('/o/').data.decode())
        # actual_response = self._request_to_dict('/o/')  # Not working ?!

        self.assertEqual(actual_response, expected_response, 'JSON does not match for list_organisations')

    @requests_mock.mock()
    def test_full_hierarchy_no_treetype(self, mock):
        lora_org_response = self._jsonfile_to_dict('tests/mocking/lora/lora_response_org_uuid.json')

        mock.get(lora.LORA_URL + 'organisation/organisation?uuid=722a3b7b-adb1-4f58-88cd-ecbdefd5014b',
                 json=lora_org_response)
        mock.get(lora.LORA_URL + 'organisation/organisationenhed?tilhoerer=722a3b7b-adb1-4f58-88cd-ecbdefd5014b',
                 json=self._jsonfile_to_dict('tests/mocking/lora/lora_response_organisation_orgEnhed_tilhoerer.json'))
        params_get_orgUnits = ''.join(['?uuid=43b5dfc7-4d8c-494f-a954-d63379ffa1f3',
                                   '&uuid=1ae72c47-b8f3-41ba-9c54-ed5c496c5bdd',
                                    '&uuid=da9491aa-123f-4218-9551-ff1fcefe4ddb'])
        mock.get(lora.LORA_URL + 'organisation/organisationenhed' + params_get_orgUnits,
                 json=self._jsonfile_to_dict('tests/mocking/lora/lora_response_organisation_orgEnhed_uuidx3.json'))
        mock.get(lora.LORA_URL + 'organisation/organisationenhed?overordnet=da9491aa-123f-4218-9551-ff1fcefe4ddb&tilhoerer=722a3b7b-adb1-4f58-88cd-ecbdefd5014b',
                 json={'results': [[]]})
        mock.get(lora.LORA_URL + 'organisation/organisationenhed?overordnet=43b5dfc7-4d8c-494f-a954-d63379ffa1f3&tilhoerer=722a3b7b-adb1-4f58-88cd-ecbdefd5014b',
                 json={'results': [[]]})

        expected_response = self._jsonfile_to_dict('tests/mocking/mo_response_full-hierarchy.json')
        actual_response = json.loads(self.app.get('/o/722a3b7b-adb1-4f58-88cd-ecbdefd5014b/full-hierarchy?effective-date=&query=').data.decode())

        self.assertEqual(actual_response, expected_response, 'JSON does not match for full_hierarchy (no treetype)')






if __name__ == '__main__':
    unittest.main()
