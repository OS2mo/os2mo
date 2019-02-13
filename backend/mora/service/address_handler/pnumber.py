#
# Copyright (c) 2017-2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from . import base


class PNumberAddressHandler(base.AddressHandler):
    scope = 'PNUMBER'
    prefix = 'urn:dk:cvr:produktionsenhed:'
