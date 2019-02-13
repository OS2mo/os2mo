#!/usr/bin/env python3
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

import setuptools

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

setuptools.setup(
    name='OS2mo',
    author='Magenta ApS',
    author_email='info@magenta.dk',
    description='OS2mo - Medarbejder og Organisation',
    license='MPL 2.0',
    version='0.14.0',
    url="https://os2mo.readthedocs.io/",
    packages=setuptools.find_packages(where=BACKEND_DIR, exclude=['tests']),
    test_loader='unittest:TestLoader',

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
