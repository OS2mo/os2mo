from . import base


class WWWAddressHandler(base.AddressHandler):
    scope = 'WWW'
    prefix = 'urn:magenta.dk:www:'
