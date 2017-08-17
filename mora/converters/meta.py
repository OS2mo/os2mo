#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import re

VERSION_PREFIX = re.compile(r'v(\d+):')


class Address(collections.namedtuple('Address', ['name', 'primary'])):
    __slots__ = ()

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


class PhoneNumber(collections.namedtuple(
        'PhoneNumber', ['location', 'visibility'],
)):
    __slots__ = ()

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
