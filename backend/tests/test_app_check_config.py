#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
import tempfile

from mora.integrations import serviceplatformen


class Tests(util.TestCase):

    def test_serviceplatformen_dummy_true(self):
        "test bad/missing values in config for Serviceplatformen "
        "are not considered in dummy mode"
        self.assertTrue(
            serviceplatformen.check_config({"DUMMY_MODE": True})
        )

    def test_serviceplatformen_dummy_false(self):
        "test bad/missing values in config for Serviceplatformen"
        with self.assertRaisesRegex(
            ValueError,
            "Serviceplatformen certificate path must be configured: "
            "SP_CERTIFICATE_PATH"
        ):
            serviceplatformen.check_config({"DUMMY_MODE": False})

        with self.assertRaises(ValueError):
            serviceplatformen.check_config({
                "DUMMY_MODE": False,
                "SP_CERTIFICATE_PATH": "",
            })

        tf = tempfile.NamedTemporaryFile()
        with self.assertRaisesRegex(
            ValueError,
            "Serviceplatformen certificate can not be empty: "
            "SP_CERTIFICATE_PATH"
        ):
            serviceplatformen.check_config({
                "DUMMY_MODE": False,
                "SP_CERTIFICATE_PATH": tf.name,
            })

        tf.close()
        with self.assertRaisesRegex(
            FileNotFoundError,
            "Serviceplatformen certificate not found: "
            "SP_CERTIFICATE_PATH"
        ):
            serviceplatformen.check_config({
                "DUMMY_MODE": False,
                "SP_CERTIFICATE_PATH": tf.name,
            })
