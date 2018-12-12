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


def ensure_lora_patched():
    try:
        # patch db_structure in case we have oio_rest/oio_common installed
        import oio_common  # noqa F401
        from oio_common import db_structure
        orgfile = pathlib.Path(db_structure.__file__)
        topdir = pathlib.Path(__file__).absolute().parent.parent.parent
        patchfile = topdir / "setup" / "db_structure.py"

        if orgfile.read_text() != patchfile.read_text():
            orgfile.write_text(patchfile.read_text())
            # reimport db_structure after patching
            import importlib
            importlib.reload(db_structure)
        return True
    except ImportError:
        # oio_common not yet present - nothing to patch
        return False


LORA_PATCHED = ensure_lora_patched()
