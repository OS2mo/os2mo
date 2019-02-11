#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import flask
import requests
import uuid

from . import base
from ... import exceptions
from ... import mapping

session = requests.Session()
session.headers = {
    'User-Agent': 'MORA',
}

NOT_FOUND = "Ukendt"


class DARAddressHandler(base.AddressHandler):
    scope = 'DAR'
    prefix = 'urn:dar:'

    def __init__(self, value):
        super().__init__(value)

        try:
            self.address_object = self._fetch_from_dar(value)
        except Exception as exc:
            self.error = {
                mapping.NAME: NOT_FOUND,
                mapping.HREF: None,
                mapping.VALUE: value,
                mapping.ERROR: str(exc),
            }

            flask.current_app.logger.warn(
                'ADDRESS LOOKUP FAILED in {!r}:\n{}'.format(
                    flask.request.url,
                    value,
                ),
            )

    @property
    def name(self):
        return ''.join(self._address_string_chunks(self.address_object))

    @property
    def href(self):
        href = (
            'https://www.openstreetmap.org/'
            '?mlon={x}&mlat={y}&zoom=16'.format(**self.address_object)
            if 'x' in self.address_object and 'y' in self.address_object
            else None
        )

        return href

    def get_mo_address_and_properties(self):
        if hasattr(self, 'error'):
            return self.error
        else:
            return super().get_mo_address_and_properties()

    @staticmethod
    def _fetch_from_dar(addrid):
        for addrtype in (
            'adresser', 'adgangsadresser',
            'historik/adresser', 'historik/adgangsadresser'
        ):
            r = session.get(
                'https://dawa.aws.dk/' + addrtype,
                # use a list to work around unordered dicts in Python < 3.6
                params=[
                    ('id', addrid),
                    ('noformat', '1'),
                    ('struktur', 'mini'),
                ],
            )

            addrobjs = r.json()

            r.raise_for_status()

            if addrobjs:
                # found, escape loop!
                break

        else:
            raise LookupError('no such address {!r}'.format(addrid))

        return addrobjs.pop()

    @staticmethod
    def _address_string_chunks(addr):
        # loosely inspired by 'adressebetegnelse' in apiSpecification/util.js
        # from https://github.com/DanmarksAdresser/Dawa/

        yield addr['vejnavn']

        if addr.get('husnr') is not None:
            yield ' '
            yield addr['husnr']

        if addr.get('etage') is not None or addr.get('dør') is not None:
            yield ','

        if addr.get('etage') is not None:
            yield ' '
            yield addr['etage']
            yield '.'

        if addr.get('dør') is not None:
            yield ' '
            yield addr['dør']

        yield ', '

        if addr.get('supplerendebynavn') is not None:
            yield addr['supplerendebynavn']
            yield ', '

        yield addr['postnr']
        yield ' '
        yield addr['postnrnavn']

    @classmethod
    def validate_value(cls, value):
        """Values should be UUID in DAR"""
        try:
            uuid.UUID(value)
        except ValueError:
            exceptions.ErrorCodes.V_INVALID_ADDRESS_DAR(
                value=value
            )
