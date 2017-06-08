#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import contextlib
import io
import os
import unittest

import pycodestyle

# upstream files; do not modify
UPSTREAM_FILES = {
    'mora/compat/secrets.py',
}

# TODO: re-enable style checks for these files as needed
SKIP_LIST = {
    'mora/converters/writing.py',
    'sandbox/LoRa/populate_LoRa.py',
    'tests/test_app.py',
    'tests/converters/writing/test_create_org_unit.py',
    'tests/converters/writing/test_create_virkning.py',
    'tests/converters/writing/test_rename_org_unit.py',
    'tests/converters/writing/test_set_virkning.py',
    'tests/utils/test_utils.py',
}


class CodeStyleTests(unittest.TestCase):

    @property
    def rootdir(self):
        return os.path.dirname(os.path.dirname(__file__))

    @property
    def source_files(self):
        """Generator that yields Python sources to test"""

        for dirpath, dirs, fns in os.walk(self.rootdir):
            dirs[:] = [
                dn for dn in dirs
                if not dn.startswith('venv-') and dn != 'node_modules'
            ]

            for fn in fns:
                fp = os.path.join(dirpath, fn)
                if fp in UPSTREAM_FILES or fn[0] == '.':
                    # skip these
                    continue
                elif fn.endswith('.py'):
                    yield os.path.relpath(fp)

    def test_style(self):
        'Test that all Python source files pass the style check'
        style = pycodestyle.StyleGuide()
        style.init_report(pycodestyle.StandardReport)

        for fn in self.source_files:
            # a subtest ensure we report each invalid file
            # independently, yet report all files in each run
            with self.subTest(fn):
                if fn in SKIP_LIST:
                    self.skipTest(fn)

                buf = io.StringIO()

                with contextlib.redirect_stdout(buf):
                    style.check_files([fn])

                if buf.getvalue():
                    self.fail("Found code style errors and/or warnings:\n" +
                              buf.getvalue())

    def test_source_files(self):
        'Sanity check: we must find multiple sources'
        sources = list(self.source_files)

        self.assertTrue(sources)
        self.assertGreater(len(sources), 1, sources)
