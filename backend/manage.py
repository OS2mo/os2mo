#!/usr/bin/env python
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Flask invocation

Customised to create and configure a virtual environment.

'''

from __future__ import print_function, absolute_import, unicode_literals

import importlib
import os
import platform
import site
import subprocess
import sys

REQUIRED_PYTHON = (3, 5)
CURRENT_PYTHON = sys.version_info[:2]

if __name__ == "__main__":
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
        if (
            CURRENT_PYTHON[0] != REQUIRED_PYTHON[0] or
            CURRENT_PYTHON[1] < REQUIRED_PYTHON[1]
        ):
            exe = 'python%d.%d' % REQUIRED_PYTHON
            try:
                os.execlp(exe, exe, *sys.argv)
            except OSError:
                try:
                    if CURRENT_PYTHON[0] == REQUIRED_PYTHON[0]:
                        raise

                    exe = 'python%d' % REQUIRED_PYTHON[0]
                    os.execlp(exe, exe, *sys.argv)
                except OSError:
                    print(
                        'Python %d.%d or later required!' % REQUIRED_PYTHON,
                        file=sys.stderr,
                    )
                    sys.exit(os.EX_UNAVAILABLE)

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

        if platform.system() == 'Windows':
            # os.execlp doesn't actually replace the current process
            # on Windows
            sys.exit(subprocess.call([venv_executable] + sys.argv))
        else:
            os.execlp(venv_executable, venv_executable, *sys.argv)

    requirements_file = ('requirements-test.txt'
                         if 'test' in sys.argv
                         else 'requirements.txt')

    r = os.fork()

    if not r:
        import pip
        pip.commands.install.InstallCommand().main([
            '-qr',
            os.path.join(basedir, requirements_file),
        ])

        sys.exit(0)

    os.wait()

    # Reload site to pick up all references to newly installed modules
    # in particular those installed with -e
    importlib.reload(site)

    os.environ.setdefault("FLASK_APP", "mora.app")
    os.environ.setdefault("FLASK_DEBUG", "1")

    from flask import cli

    sys.exit(cli.main())
