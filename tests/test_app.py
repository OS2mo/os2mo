import unittest
import mora.app as mora
import requests_mock
import json
from mora import lora


class MoraTestCase(unittest.TestCase):
    def setUp(self):
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()

    def tearDown(self):
        pass

    # Careful here - test code must not be "complicated"...
    def _json_to_dict(self, path):
        """
        Reads JSON from resources folder and converts to Python dictionary
        :param path: path to json resource 
        :return: dictionary corresponding to the resource JSON
        """
        with open(path) as f:
            lines = f.readlines()
        json_str = ''.join(lines)
        return json.loads(json_str)

    def test_acl(self):
        rv = self.app.get('/acl/')
        assert b'[]\n' == rv.data

    @requests_mock.mock()
    def test_list_organisations(self, mock):
        lora_response = self._json_to_dict('tests/resources/lora_response_get_organisation_from_uuid.json')

        mock.get(lora.LORA_URL + 'organisation/organisation?bvn=%', json={'results': [['f58a99a5-a34f-4c6a-8fb2-118a2e25eacb']]})
        mock.get(lora.LORA_URL + 'organisation/organisation?uuid=f58a99a5-a34f-4c6a-8fb2-118a2e25eacb', json=lora_response)

        expected_response = self._json_to_dict('tests/resources/mo_response_list_organisations.json')
        actual_response = json.loads(self.app.get('/o/').data.decode())

        self.assertEquals(actual_response, expected_response, 'JSON does not match for list_organisations')


if __name__ == '__main__':
    unittest.main()