# -- coding: utf-8 --

from os2mo_data_import.adapters.base import MoxUtility, MemoryMap
from os2mo_data_import.adapters.mo_types import OrganisationUnit

class Organisation(MoxUtility):

    storage = {}

    def __init__(self, org_name, bvn=None, municipality_code=999,
                uuid=None, date_from=None, date_to=None):

        if uuid:
            self.uuid = uuid
        else:
            self.uuid = self.create_uuid()

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
                    "virkning": self.validity_range(date_from, date_to)
                }
            ]
        }

        relationer = {
            "myndighed": [
                {
                    "urn": urn_municipality_code,
                    "virkning": self.validity_range(date_from, date_to)
                }
            ]
        }

        tilstande = {
            "organisationgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": self.validity_range(date_from, date_to)
                }
            ]
        }

        return {
            "note": "Automatisk indlæsning",
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }

    def __repr__(self):
        return self.uuid


class Facet(MemoryMap):

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier):

        data = self.build_payload(
            bvn=identifier,
            parent_org=self.parent_org
        )

        return self.save(identifier, data)

    def build_payload(self, bvn, parent_org, from_date=None, to_date=None):

        default_type = "organisation"
        default_tilhoerer = "klassifikation"

        # Build payload
        attributter = {
            "facetegenskaber": [
                {
                    "brugervendtnoegle": str(bvn),
                    "virkning": self.validity_range(from_date, to_date)
                }
            ]
        }

        relationer = {
            "ansvarlig": [
                {
                    "objekttype": default_type,
                    "uuid": parent_org,
                    "virkning": self.validity_range(from_date, to_date)
                }
            ],
            "facettilhoerer": [
                {
                    "objekttype": default_tilhoerer,
                    "virkning": self.validity_range(from_date, to_date)
                }
            ]
        }

        tilstande = {
            "facetpubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": self.validity_range(from_date, to_date)
                }
            ]
        }

        return {
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }


class Klasse(MemoryMap):

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def add(self, identifier, **kwargs):

        data = self.build_payload(
            user_key=identifier,
            **kwargs
        )

        return self.save(identifier, data)

    def build_payload(self, user_key, facet_ref,
                      from_date=None, to_date=None, **properties):

        klasse_properties = {
            "brugervendtnoegle": user_key,
            "virkning": validity_range(from_date, to_date)
        }

        if properties:
            klasse_properties.update(properties)

        attributter = {
            "klasseegenskaber": [
                klasse_properties
            ]
        }

        relationer = {
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": self.parent_org,
                    "virkning": validity_range(from_date, to_date)
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facet_ref,
                    "virkning": validity_range(from_date, to_date)
                }
            ]
        }

        tilstande = {
            "klassepubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": validity_range(from_date, to_date)
                }
            ]
        }

        return {
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
        }


