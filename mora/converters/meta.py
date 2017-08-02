#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re


class Address(object):
    __slots__ = ('name', 'primary')

    VERSION_PREFIX = re.compile(r'v(\d+):')

    def __init__(self, name: str, primary: bool):
        self.name = name
        self.primary = primary

    @classmethod
    def fromdict(cls, d):
        return cls(
            name=d['name'],
            primary=d['primaer'],
        )

    @classmethod
    def fromstring(cls, s):
        if not s:
            primary, name = '0', ''
        elif not cls.VERSION_PREFIX.match(s):
            primary, name = '0', s
        elif s.startswith('v0:'):
            primary, name = s.split(':', 2)[1:]
        else:
            raise ValueError('unsupported Address version: ' + s)

        return cls(name, primary == '1')

    def __str__(self):
        return 'v0:{:d}:{:s}'.format(self.primary, self.name)
