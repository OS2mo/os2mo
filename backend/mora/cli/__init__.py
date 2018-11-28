#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import sys

# Can't do monkeypatching only because file is used as program
try:
    # first file patching in case we have test module installed:
    import oio_common
    from oio_common import db_structure
    orgfile = db_structure.__file__
    backenddir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    topdir = os.path.dirname(backenddir)
    patchfile = os.path.join(topdir, 'setup', "db_structure.py")
    if not open(orgfile).read() == open(patchfile).read():
        open(orgfile, "w").write(open(patchfile).read())
        # monkeypatching necessary for
        # first time running tests (jenkins)
        sys.path.insert(0, os.path.join(topdir, 'setup'))
        import db_structure as new_db_structure
        oio_common.db_structure = new_db_structure
        sys.path.pop(0)
except ImportError:
    pass  # oio_common not yet present - nothing to patch


from . import base  # noqa
from . import lora  # noqa
