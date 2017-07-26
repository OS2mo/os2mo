#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import contextlib
import io
import itertools
import os
import unittest

import pycodestyle

from . import util

# upstream files; do not modify
UPSTREAM_FILES = {
    'mora/compat/secrets.py',
}

# TODO: re-enable style checks for these files as needed
SKIP_LIST = {
    'tests/test_app.py',
}

SKIP_DIRS = {
    'sandbox',
    'node_modules',
    'bower_components',
}


class CodeStyleTests(unittest.TestCase):

    @property
    def rootdir(self):
        return os.path.dirname(os.path.dirname(__file__))

    @property
    def source_files(self):
        """Generator that yields Python sources to test"""

        for dirpath, dirs, fns in os.walk(self.rootdir):
            if 'pip-selfcheck.json' in fns:
                dirs[:] = []
                continue

            dirs[:] = [
                dn for dn in dirs
                if dn not in SKIP_DIRS
            ]

            for fn in fns:
                fp = os.path.join(dirpath, fn)
                if fp in UPSTREAM_FILES or fn[0] == '.':
                    # skip these
                    continue
                elif fn.endswith('.py'):
                    yield os.path.relpath(fp)

    def test_license_headers(self):
        'Test that all Python source files begin with our license header'

        with open(__file__) as fp:
            header = ''.join(itertools.takewhile((lambda l: l.startswith('#')),
                                                 fp))

        missing = []

        for fn in self.source_files:
            with open(fn) as fp:
                text = fp.read()

                # no need to assert our rights to empty files...
                if text and header not in text:
                    missing.append(fn)

        self.assertEqual(missing, [], 'files missing license header!')

    def test_style(self):
        'Test that all Python source files pass the style check'
        style = pycodestyle.StyleGuide(ignore='N/A')
        style.init_report(pycodestyle.StandardReport)

        for fn in self.source_files:
            if os.path.relpath(fn, util.BASE_DIR) in SKIP_LIST:
                continue

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
