import unittest
from service_person_stamdata_udvidet.helpers import validate_cprnr

class TestHelpers(unittest.TestCase):

    def test_cpr_should_pass(self):

        cpr_value = "1234567890"

        # Expect to pass
        self.assertTrue(validate_cprnr(cpr_value))


    def test_cpr_too_long_should_fail(self):

        cpr_value = "1234567890111"

        # Expect to fail
        self.assertFalse(validate_cprnr(cpr_value))


    def test_cpr_too_short_should_fail(self):

        cpr_value = "123456"

        # Expect to fail
        self.assertFalse(validate_cprnr(cpr_value))

if __name__ == '__main__':
    unittest.main()
