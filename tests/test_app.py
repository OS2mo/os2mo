import os
import unittest
import tempfile
# from mora import mora

class MoraTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        # mora.app.config['TESTING'] = True
        # self.app = mora.app.test_client()
        # with flaskr.app.app_context():
        #     flaskr.init_db()
        pass

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(flaskr.app.config['DATABASE'])
        pass

    def test_dummy(self):
        assert True

if __name__ == '__main__':
    unittest.main()