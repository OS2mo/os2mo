import requests
from . import base
from ... import mapping

session = requests.Session()

NOT_FOUND = "Ukendt"


class DARAddressHandler(base.AddressHandler):
    scope = 'DAR'
    prefix = 'urn:dar:'

    def __init__(self, value):
        super().__init__(value)

        try:
            self.address_object = self._fetch_from_dar(value)
        except Exception as exc:
            self.address_object = {
                mapping.NAME: NOT_FOUND,
                mapping.HREF: None,
                mapping.UUID: value,
                mapping.ERROR: str(exc),
            }

    def get_pretty_value(self):
        return ''.join(self._address_string_chunks(self.address_object))

    def get_href(self):
        href = (
            'https://www.openstreetmap.org/'
            '?mlon={x}&mlat={y}&zoom=16'.format(**self.address_object)
            if 'x' in self.address_object and 'y' in self.address_object
            else None
        )

        return href

    def get_mo_address(self):
        if self.address_object.get(mapping.ERROR):
            return self.address_object
        else:
            return super().get_mo_address()

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
