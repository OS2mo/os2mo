#
# Copyright (c) 2017-2018, Magenta ApS
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

from . import util

import pycodestyle

# upstream files; do not modify
UPSTREAM_FILES = {
}

# TODO: re-enable style checks for these files as needed
SKIP_LIST = {
    'tests/test_selenium.py',
}

SKIP_DIRS = {
    'sandbox',
    'node_modules',
    'bower_components',
    'mox'
}


class CodeStyleTests(unittest.TestCase):

    @property
    def rootdir(self):
        return os.path.dirname(os.path.dirname(__file__))

    @property
    def source_files(self):
        """Generator that yields Python sources to test"""

        for dirpath, dirs, fns in os.walk(self.rootdir):
            reldirpath = os.path.relpath(dirpath, self.rootdir)

            if 'pip-selfcheck.json' in fns or 'pyvenv.cfg' in fns:
                dirs[:] = []
                continue

            dirs[:] = [
                dn for dn in dirs
                if dn not in SKIP_DIRS
            ]

            for fn in fns:
                if (
                        fn[0] == '.' or
                        os.path.join(reldirpath, fn) in UPSTREAM_FILES
                ):
                    # skip these
                    continue
                elif fn.endswith('.py'):
                    yield os.path.relpath(os.path.join(dirpath, fn))

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
                    missing.append('\n')

        self.assertEqual('', ''.join(missing), 'files missing license header!')

    def test_style(self):
        'Test that all Python source files pass the style check'
        style = pycodestyle.StyleGuide(ignore='N/A')
        style.init_report(pycodestyle.StandardReport)

        with contextlib.redirect_stdout(io.StringIO()) as buf:
            report = style.check_files(
                fn for fn in self.source_files
                if os.path.relpath(fn, util.BASE_DIR) not in SKIP_LIST
            )

        self.assertFalse(
            report.total_errors,
            "Found code style errors and/or warnings:\n\n" + buf.getvalue(),
        )

    def test_source_files(self):
        'Sanity check: we must find multiple sources'
        sources = list(self.source_files)

        self.assertTrue(sources)
        self.assertGreater(len(sources), 1, sources)
