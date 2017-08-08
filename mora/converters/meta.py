#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re

VERSION_PREFIX = re.compile(r'v(\d+):')


class Address(object):
    __slots__ = ('name', 'primary')

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
        elif not VERSION_PREFIX.match(s):
            primary, name = '0', s
        elif s.startswith('v0:'):
            primary, name = s.split(':', 2)[1:]
        else:
            raise ValueError('unsupported Address version: ' + s)

        return cls(name, primary == '1')

    def __str__(self):
        return 'v0:{:d}:{:s}'.format(self.primary, self.name)


PHONE_PREFIX = 'urn:magenta.dk:telefon:'
PHONE_NUMBER_DESC = 'Telefonnummer'

PHONE_VISIBILITIES = {
    "internal": "Må vises internt",
    "external": "Må vises eksternt",
    "secret": "Hemmeligt",
}

PHONE_VISIBILITY_UUIDS = {
    "internal": "ab68b2c2-8ffb-4292-a938-60e3afe0cad0",
    "external": "c67d7315-a0a2-4238-a883-f33aa7ddabc2",
    "secret": "8d37a1ec-3d58-461f-821f-c2a7bb6bc861",
}

DEFAULT_PHONE_VISIBILITY = 'internal'


class PhoneNumber(object):
    __slots__ = ('location', 'visibility')

    def __init__(self, location: str, visibility: str):
        self.location = location
        self.visibility = visibility

    @classmethod
    def fromstring(cls, s):
        if not s:
            visibility, location = DEFAULT_PHONE_VISIBILITY, None
        elif s.startswith('v0:'):
            visibility, location = s.split(':', 2)[1:]
        else:
            raise ValueError('unsupported PhoneNumber version: ' + s)

        return cls(location, visibility)

    def __str__(self):
        return 'v0:{:s}:{:s}'.format(self.visibility, self.location)
