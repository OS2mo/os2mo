from . import base


class EmailAddressHandler(base.AddressHandler):
    scope = 'EMAIL'
    prefix = 'urn:mailto:'

    def get_href(self):
        return "mailto:{}".format(self.value)
