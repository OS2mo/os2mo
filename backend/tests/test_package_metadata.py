#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import re
import subprocess
import sys
import unittest

from . import util


class VersionTest(unittest.TestCase):
    @property
    def readme_version(self):
        with open(os.path.join(util.TOP_DIR, 'NEWS.rst')) as fp:
            all_versions = re.findall(r'^Version ([^,]*), [-\d]+$',
                                      fp.read(),
                                      re.MULTILINE)

        return all_versions[0]

    @property
    def package_version(self):
        main_version = subprocess.check_output(
            [
                sys.executable,
                os.path.join(util.BASE_DIR, 'setup.py'),
                '--version',
            ],
        )

        return main_version.decode('ascii').strip()

    @property
    def frontend_version(self):
        frontend_info = util.jsonfile_to_dict(
            os.path.join(util.FRONTEND_DIR, 'package.json'),
        )

        return frontend_info['version']

    def test_versions(self):
        self.assertEqual(self.readme_version, self.package_version)
        self.assertEqual(self.readme_version, self.frontend_version)
