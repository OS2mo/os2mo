#!/usr/bin/env python3
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import distutils
import json
import os
import shutil
import subprocess
import sys

from distutils.command.build import build
from distutils.command.install import install
from distutils import log

import setuptools

BASEDIR = os.path.dirname(__file__)

with open(os.path.join(BASEDIR, 'package.json')) as fp:
    node_data = json.load(fp)


class build_frontend(build):

    description = "build the frontend"

    def run(self):
        if not shutil.which('yarn'):
            log.warn('skipping frontend build!')
            return

        log.info('running "yarn"')
        subprocess.check_call(['yarn'], cwd=BASEDIR)

        log.info('running "yarn build"')
        subprocess.check_call(['yarn', 'build'], cwd=BASEDIR)


class build_data(build):

    description = "build the documentation"

    def run(self):
        import flask
        from mora import app

        docdir = os.path.join(BASEDIR, 'docs')
        blueprintdir = os.path.join(docdir, 'blueprints')

        os.makedirs(blueprintdir, exist_ok=True)

        with app.app.app_context():
            for blueprint in app.app.iter_blueprints():
                destfile = os.path.join(blueprintdir, blueprint.name + '.rst')
                log.info('generating ' + destfile)

                with open(destfile, 'w') as fp:
                    fp.write(flask.render_template('blueprint.rst',
                                                   blueprint=blueprint))

            destfile = os.path.join(docdir, 'backend.rst')
            log.info('generating ' + destfile)

            with open(destfile, 'w') as fp:
                modules = sorted(m for m in sys.modules
                                 if m.split('.', 1)[0] == 'mora')
                fp.write(flask.render_template('backend.rst',
                                               modules=modules))


class mobuild(build):
    sub_commands = build.sub_commands + [
        ('build_data', None),
        ('build_frontend', None),
    ]


class moinstall(install):
    sub_commands = install.sub_commands + [
        ('build_data', None),
    ]


setuptools.setup(
    name=node_data['name'],
    author='Magenta ApS',
    author_email='info@magenta.dk',
    description=node_data['description'],
    license='MPL 2.0',
    version=node_data['version'],
    url="https://mora.readthedocs.io/",
    cmdclass={
        'build_frontend': build_frontend,
        'build_data': build_data,
        'build': mobuild,
        'install': moinstall,
    },
    packages=setuptools.find_packages(exclude=['tests']),

    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
