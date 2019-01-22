from . import base


class EANAddressHandler(base.AddressHandler):
    scope = 'EAN'
    prefix = 'urn:magenta.dk:ean:'
