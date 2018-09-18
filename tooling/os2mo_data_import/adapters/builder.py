# -- coding: utf-8 --

from os2mo_data_import.adapters.base import MoxUtility, MemoryMap
from os2mo_data_import.adapters.mo_types import OrganisationUnit, Employee


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
        self.employee = Employee(self.uuid)

        # Create defaults
        facet_map = self.facet.create_defaults()

        # Default klasse requires a (dict) map of all facet types
        self.klasse.create_defaults(facet_map)

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

    __default_types__ = [
        "Tilknytningstype",
        "Funktionstype",
        "Lederansvar",
        "Lederniveau",
        "Brugertype",
        "Engagementstype",
        "Enhedstype",
        "Ledertyper",
        "Orlovstype",
        "Myndighedstype",
        "Rolletype",
        "Stillingsbetegnelse",
        "Adressetype"
    ]

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def create_defaults(self, default_types=[]):

        if not isinstance(default_types, list):
            raise TypeError("Default types must be declared as a list")

        # Overwrite if available
        if default_types:
            self.__default_types__ = default_types

        for default_value in self.__default_types__:
            self.add(default_value)

        return self.get_map()

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

    __default_types__ = [
        {
            "brugervendtnoegle": "Enhed",
            "beskrivelse": "Dette er en organisationsenhed",
            "titel": "Enhed",
            "facet_type": "Enhedstype"
        },
        {
            "brugervendtnoegle": "AdressePost",
            "eksempel": "<UUID>",
            "omfang": "DAR",
            "titel": "Adresse",
            "facet_type": "Adressetype"
        },
        {
            "brugervendtnoegle": "Email",
            "eksempel": "test@example.com",
            "omfang": "EMAIL",
            "titel": "Emailadresse",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Telefon",
            "eksempel": "20304060",
            "omfang": "PHONE",
            "titel": "Telefonnummer",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Webadresse",
            "eksempel": "http://www.magenta.dk",
            "omfang": "WWW",
            "titel": "Webadresse",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "EAN",
            "eksempel": "00112233",
            "omfang": "EAN",
            "titel": "EAN nr.",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "PNUMBER",
            "eksempel": "00112233",
            "omfang": "PNUMBER",
            "titel": "P-nr.",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "TEXT",
            "eksempel": "Fritekst",
            "omfang": "TEXT",
            "titel": "Fritekst",
            "facet_type": "Adressetype",
        },
        {
            "brugervendtnoegle": "Ansat",
            "facet_type": "Engagementstype"
        },
        {
            "brugervendtnoegle": "Leder",
            "titel": "Leder",
            "facet_type": "Ledertyper",
        },
        {
            "brugervendtnoegle": "Lederansvar",
            "titel": "Ansvar for organisationsenheden",
            "facet_type": "Lederansvar",
        },
        {
            "brugervendtnoegle": "Lederniveau",
            "titel": "Niveau 90",
            "facet_type": "Lederniveau",
        },
    ]

    def __init__(self, parent_org):
        self.parent_org = parent_org
        self.storage_map = {}

    def create_defaults(self, facet_references):

        # Create map for later use
        self.map = facet_references

        for default_type in self.__default_types__:
            identifier = default_type["brugervendtnoegle"]

            # Reference
            facet_type = default_type["facet_type"]
            del default_type["facet_type"]

            facet_ref = self.map.get(facet_type)

            self.add(identifier, facet_ref, default_type)

        return self.get_map()

    def add(self, identifier, facet_ref, properties):

        if not isinstance(properties, dict):
            raise TypeError("Added properties must be of type dict")

        data = self.build_payload(
            user_key=identifier,
            facet_ref=facet_ref,
            **properties
        )

        return self.save(identifier, data)

    def build_payload(self, user_key, facet_ref,
                      from_date=None, to_date=None, **properties):

        klasse_properties = {
            "brugervendtnoegle": user_key,
            "virkning": self.validity_range(from_date, to_date)
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
                    "virkning": self.validity_range(from_date, to_date)
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facet_ref,
                    "virkning": self.validity_range(from_date, to_date)
                }
            ]
        }

        tilstande = {
            "klassepubliceret": [
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
