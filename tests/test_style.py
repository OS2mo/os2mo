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
                if not dn.startswith('venv-')
            ]

            for fn in fns:
                if fn[0] != '.' and fn.endswith('.py'):
                    yield os.path.relpath(os.path.join(dirpath, fn))

    @unittest.expectedFailure
    def test_style(self):
        'Test that all Python source files pass the style check'
        style = pycodestyle.StyleGuide()
        style.init_report(pycodestyle.StandardReport)

        for fn in self.source_files:
            # a subtest ensure we report each invalid file
            # independently, yet report all files in each run
            with self.subTest(fn):
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
