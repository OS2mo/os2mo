# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from lora_connector import __version__


def test_version():
    assert __version__ == '0.1.0'
