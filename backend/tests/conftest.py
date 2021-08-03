# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os


def pytest_runtest_setup(item):
    print(os.environ.items())
    os.environ['PYTEST_RUNNING'] = 'True'
