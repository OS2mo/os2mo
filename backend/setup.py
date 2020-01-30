#!/usr/bin/env python3


# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import io
import os
import re

import setuptools


BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
__init___path = os.path.join(BACKEND_DIR, "mora", "__init__.py")
# this is the way flask does it
with io.open(__init___path, "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)


setuptools.setup(
    name='OS2mo',
    author='Magenta ApS',
    author_email='info@magenta.dk',
    description='OS2mo - Medarbejder og Organisation',
    license='MPL 2.0',
    version=version,
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
