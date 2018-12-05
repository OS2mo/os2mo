#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import sys
import pathlib

try:
    # patch db_structure in case we have oio_rest/oio_common installed
    import oio_common  # noqa F401
    from oio_common import db_structure
    orgfile = pathlib.Path(db_structure.__file__)
    topdir = pathlib.Path(__file__).absolute().parent.parent.parent
    patchfile = topdir / "setup" / "db_structure.py"

    orgfile.write_text(patchfile.read_text())

    # reimport db_structure after patching
    import importlib
    importlib.reload(db_structure)

    # regenerate 'generated-files' necessary first time
    # apply-templates has that side effect when imported
    oio_rest_top = orgfile.parent.parent
    src = oio_rest_top / "apply-templates.py"
    dst = oio_rest_top / "apply_templates.py"

    # insert path for import of apply-templates
    sys.path.insert(0, str(oio_rest_top))

    # temporarily symlink to importable name
    if not dst.exists():
        os.symlink(str(src), str(dst))

    # import for side effect
    import apply_templates  # noqa 401

    if src.exists():
        os.unlink(str(dst))

    # remove import path again
    sys.path.remove(str(oio_rest_top))

except ImportError:
    pass  # oio_common not yet present - nothing to patch
