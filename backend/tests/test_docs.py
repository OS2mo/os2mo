#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from . import util


class Tests(unittest.TestCase):
    maxDiff = None

    def test_is_vuedoc_uptodate(self):
        '''Check whether the VueDoc-generated files are up-to-date.'''

        srcdir = os.path.join(util.FRONTEND_DIR, 'src')
        docdir = os.path.join(util.DOCS_DIR, 'vuedoc')
        tempdir = tempfile.mkdtemp(prefix='mo-vuedoc-')

        sources = [
            os.path.join(dirpath, filename)
            for dirpath, dirnames, filenames in os.walk(srcdir)
            for filename in filenames
            if os.path.splitext(filename)[1] in ('.vue',)
        ]

        subprocess.check_call(
            [
                os.path.join(util.FRONTEND_DIR,
                             'node_modules', '.bin', 'vuedoc.md'),
                '--output', tempdir,
                *sources,
            ],
            cwd=util.FRONTEND_DIR,
        )

        comparator = filecmp.dircmp(docdir, tempdir)

        proc = subprocess.run(
            ['diff', '-Naur', docdir, tempdir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        sys.stdout.write(proc.stdout.decode())
        sys.stderr.write(proc.stderr.decode())

        msg = '''
        To fix this, run:
        rm -r {docdir} && mv {tempdir} {docdir}
        '''.format(**locals())

        print(msg, file=sys.stderr)

        self.assertEquals(proc.returncode, 0)

        shutil.rmtree(tempdir)
