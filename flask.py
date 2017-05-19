#!/usr/bin/env python
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Flask invocation

Customised to create and configure a virtual environment.

'''

from __future__ import print_function, absolute_import, unicode_literals, division

import base64
import os
import platform
import subprocess
import sys

REQUIRED_PYTHON = (3, 5)
CURRENT_PYTHON = sys.version_info[:2]

if __name__ != "__main__":
    # rejigger the path a bit so that this file -- flask.py -- doesn't
    # shadow the flask package
    assert not __package__

    origpath = sys.path[:]
    sys.path.remove(os.path.dirname(__file__))
    del sys.modules[__name__]

    import importlib
    importlib.import_module(__name__, __package__)

    sys.path = origpath

else:
    basedir = os.path.abspath(os.path.dirname(__file__))

    # allow testing on different platforms and VMs
    venvdir = os.path.join(basedir, "venv-{}-{}-{}.{}".format(
        platform.system(), platform.python_implementation(),
        *platform.python_version_tuple()[:2]
    ).lower())

    # commonpath() is Python 3.5+, so first, check for the platform
    is_in_venv = (
        REQUIRED_PYTHON <= CURRENT_PYTHON and
        (os.path.splitdrive(sys.executable)[0] ==
         os.path.splitdrive(basedir)[0]) and
        os.path.commonpath([sys.executable, basedir]) == basedir
    )

    venv_executable = (os.path.join(venvdir, 'bin', 'python')
                       if platform.system() != 'Windows'
                       else os.path.join(venvdir, 'Scripts', 'python.exe'))

    # create the virtual env, if necessary
    if not is_in_venv:
        if (CURRENT_PYTHON[0] != REQUIRED_PYTHON[0] or
                CURRENT_PYTHON[1] < REQUIRED_PYTHON[1]):
            exe = 'python%d.%d' % REQUIRED_PYTHON
            os.execlp(exe, exe, *sys.argv)

        if not os.path.isfile(venv_executable):
                import venv

                try:
                    venv.main(['--upgrade', venvdir])
                except SystemExit:
                    # handle Ubuntu's horrible hackery where you get a
                    # venv without pip...
                    import shutil
                    shutil.rmtree(venvdir)
                    raise

        subprocess.check_call([
            venv_executable, '-m', 'pip', 'install', '-qr', 'requirements.txt',
        ])

        if platform.system() == 'Windows':
            # os.execlp doesn't actually replace the current process
            # on Windows
            sys.exit(subprocess.call([venv_executable] + sys.argv))
        else:
            os.execlp(venv_executable, venv_executable, *sys.argv)

    os.environ.setdefault("FLASK_APP", "mora.app")
    os.environ.setdefault("FLASK_DEBUG", "1")

    from flask import cli

    sys.exit(cli.main())
