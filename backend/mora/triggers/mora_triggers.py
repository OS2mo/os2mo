#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""
main entrypoint for built-in triggers
import modules with decorated triggers here in the sequence You want them run
"""

from . import amqp_trigger  # noqa activate triggers
