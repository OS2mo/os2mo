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

from . import base
from ..validation.validator import forceable
from ... import exceptions
from ... import mapping
from ... import util

session = requests.Session()
session.headers = {
    'User-Agent': 'MORA',
}

NOT_FOUND = "Ukendt"


class DARAddressHandler(base.AddressHandler):
    scope = 'DAR'
    prefix = 'urn:dar:'

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
            address_object = handler._fetch_from_dar(value)
            handler._name = ''.join(
                handler._address_string_chunks(address_object))
            handler._href = (
                'https://www.openstreetmap.org/'
                '?mlon={x}&mlat={y}&zoom=16'.format(**address_object)
                if 'x' in address_object and 'y' in address_object
                else None
            )
        except LookupError:
            flask.current_app.logger.warning(
                'ADDRESS LOOKUP FAILED in {!r}: {}'.format(
                    flask.request.url,
                    value,
                ),
            )

            handler._name = NOT_FOUND
            handler._href = None

        return handler

    @classmethod
    def from_request(cls, request):
        """
        Initialize handler from MO object

        If lookup in DAR fails, this will raise an exception as we do not want
        to save an invalid object to LoRa.
        This lookup can be circumvented if the 'force' flag is used.
        """
        value = util.checked_get(request, mapping.VALUE, "", required=True)
        cls.validate_value(value)
        handler = cls(value)
        handler._href = None
        handler._name = value
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
            try:
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
            # The request mocking library throws a pretty generic exception
            # catch and rethrow as something we know how to manage
            except Exception as e:
                raise LookupError(str(e)) from e

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
    @forceable
    def validate_value(value):
        """Values should be UUID in DAR"""
        try:
            uuid.UUID(value)
            DARAddressHandler._fetch_from_dar(value)
        except (ValueError, LookupError):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_DAR(
                value=value
            )
