#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import flask
import requests
import uuid

from ... import mapping
from ... import util
from ... import exceptions
from . import base

session = requests.Session()
session.headers = {
    'User-Agent': 'MORA',
}

NOT_FOUND = "Ukendt"


class DARAddressHandler(base.AddressHandler):
    scope = 'DAR'
    prefix = 'urn:dar:'

    def _fetch_and_initialize(self, value):
        try:
            self.address_object = self._fetch_from_dar(value)
            self._name = ''.join(
                self._address_string_chunks(self.address_object))
            self._href = (
                'https://www.openstreetmap.org/'
                '?mlon={x}&mlat={y}&zoom=16'.format(**self.address_object)
                if 'x' in self.address_object and 'y' in self.address_object
                else None
            )
        except Exception as e:
            flask.current_app.logger.warning(
                'ADDRESS LOOKUP FAILED in {!r}:\n{}'.format(
                    flask.request.url,
                    value,
                ),
            )
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                "DAR Address lookup failed",
                e=str(e),
            )

    @classmethod
    def from_effect(cls, effect):
        """
        Initialize handler from LoRa object

        If the saved address fails lookup in DAR for whatever reason, handle
        gracefully and return _some_ kind of result
        """
        # Cut off the prefix
        urn = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('urn')
        value = urn[len(cls.prefix):]
        handler = cls(value)

        try:
            handler._fetch_and_initialize(value)
        except exceptions.HTTPException:
            handler.address_object = {}
            handler._name = NOT_FOUND
            handler._href = None

        return handler

    @classmethod
    def from_request(cls, request):
        """
        Initialize handler from MO object

        If lookup in DAR fails, this will raise an exception as we do not want
        to save a partial object to LoRa
        """
        value = util.checked_get(request, mapping.VALUE, "", required=True)
        handler = cls(value)
        handler._fetch_and_initialize(value)
        return handler

    @property
    def name(self):
        return self._name

    @property
    def href(self):
        return self._href

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

    @staticmethod
    def validate_value(value):
        """Values should be UUID in DAR"""
        try:
            uuid.UUID(value)
        except ValueError:
            exceptions.ErrorCodes.V_INVALID_ADDRESS_DAR(
                value=value
            )
