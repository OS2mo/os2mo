# -- coding: utf-8 --

from uuid import uuid4
from os2mo_data_import.data_types import Facet, Klasse, OrganisationUnit

def create_uuid():
    """
    Generates a UUID (version 4)
    Helper function

    :return:    UUID
    :rtype:     str
    """

    identifier = uuid4()
    return str(identifier)


def validity_range(from_date, to_date):
    if not from_date:
        from_date = "1900-01-01"

    if not to_date:
        to_date = "infinity"

    return {
        "from": from_date,
        "to": to_date
    }


class Organisation:

    def __init__(self, org_name, bvn=None, municipality_code=999,
            date_from=None, date_to=None):

        self.uuid = create_uuid()

        if not bvn:
            bvn = org_name

        self.data = self.build_payload(
            bvn=bvn,
            name=org_name,
            municipality_code=municipality_code,
            date_from=date_from,
            date_to=date_to
        )

        self.facet = Facet(self.uuid)
        self.klasse = Klasse(self.uuid)
        self.org_unit = OrganisationUnit(self.uuid)

    def build_payload(self, bvn, name, municipality_code=999, date_from=None, date_to=None):
        # Inelegant conversion to string
        municipality_code = str(municipality_code)

        # Create urn value
        urn_municipality_code = "urn:dk:kommune:{}".format(municipality_code)

        attributter = {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": str(bvn),
                    "organisationsnavn": str(name),
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        relationer = {
            "myndighed": [
                {
                    "urn": urn_municipality_code,
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        tilstande = {
            "organisationgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        return {
            "note": "Automatisk indlæsning",
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }

    def __str__(self):
        return self.uuid

if __name__ == "__main__":
    org = Organisation("Næstved", "Næstved Kommune")

    enhedstype_f = org.facet.add("Enhedstype")
    adressetype_f = org.facet.add("Adressetype")

    for facet in org.facet.db_export():
        print(facet)

