import os
import sys
import unittest
import tempfile
import mora.app as mora
import requests
import requests_mock
# from unittest.mock import patch

from mora import lora

class MoraTestCase(unittest.TestCase):
    def setUp(self):
        # self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        mora.app.config['TESTING'] = True
        self.app = mora.app.test_client()
        # with flaskr.app.app_context():
        #     flaskr.init_db()
        pass

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(flaskr.app.config['DATABASE'])
        pass

    def test_acl(self):
        rv = self.app.get('/acl/')
        assert b'[]\n' == rv.data

    def test_root(self):
        pass

    @requests_mock.mock()
    def test_list_organisations(self, m):
        m.get(lora.LORA_URL + 'organisation/organisation?bvn=%25', json={'results': []})
        self.assertEquals(self.app.get('/o').text, 'data',
                        'you fool')
        pass

if __name__ == '__main__':
    unittest.main()