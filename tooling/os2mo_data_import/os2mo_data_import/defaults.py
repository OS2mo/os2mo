#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""
Default facet and klasse types needed in order for os2mo to work.
As a minimum - at least one klasse type per facet type must be created.

Additionally there are 2 magic types which MUST be present:

 - A klasse type with the user_key: Telefon
 - A klasse type with the user_key: AdressePost

The frontend GUI depends on these 2 klasse types to exist,
as they are used as a default input field type in the frontend

TODO: Create validation for missing any missing klasse types
TODO: Default types should only be added if not created by the user
"""

# Facet types are simple as they only require a user_key to be generated
# NOTE: There should not be any cases where a custom facet type is needed.

facet_types = [
    "Engagementstype",
    "Stillingsbetegnelse",
    "Rolletype",
    "Tilknytningstype",
    "Enhedstype",
    "Orlovstype",
    "Ledertyper",
    "Lederansvar",
    "Lederniveau",
    "Adressetype",
    "Lederadressetype"
]

klasse_types = [
    (
        "Enhed", "Enhedstype",
        {
            "user_key": "Enhed",
            "description": "Dette er en organisationsenhed",
            "title": "Enhed"
        }
    ),
    (
        "AdressePost", "Adressetype",
        {
            "user_key": "AdressePost",
            "example": "<UUID>",
            "scope": "DAR",
            "title": "Adresse"
        }
    ),
    (
        "Email", "Adressetype",
        {
            "user_key": "Email",
            "example": "test@example.com",
            "scope": "EMAIL",
            "title": "Email"
        }
    ),
    (
        "Telefon", "Adressetype",
        {
            "user_key": "Telefon",
            "example": "20304060",
            "scope": "PHONE",
            "title": "Tlf"
        }
    ),
    (
        "Webadresse", "Adressetype",
        {
            "user_key": "Webadresse",
            "example": "http://www.magenta.dk",
            "scope": "WWW",
            "title": "Webadresse"
        }
    ),
    (
        "LederAdressePost", "Lederadressetype",
        {
            "user_key": "LederAdressePost",
            "example": "<UUID>",
            "scope": "DAR",
            "title": "Adresse"
        }
    ),
    (
        "LederEmail", "Lederadressetype",
        {
            "user_key": "LederEmail",
            "example": "test@example.com",
            "scope": "EMAIL",
            "title": "Email"
        }
    ),
    (
        "LederTelefon", "Lederadressetype",
        {
            "user_key": "LederTelefon",
            "example": "20304060",
            "scope": "PHONE",
            "title": "Tlf"
        }
    ),
    (
        "LederWebadresse", "Lederadressetype",
        {
            "user_key": "LederWebadresse",
            "example": "http://www.magenta.dk",
            "scope": "WWW",
            "title": "Webadresse"
        }
    ),
    (
        "EAN", "Adressetype",
        {
            "user_key": "EAN",
            "example": "00112233",
            "scope": "EAN",
            "title": "EAN-nr."
        }
    ),
    (
        "PNUMBER", "Adressetype",
        {
            "user_key": "PNUMBER",
            "example": "00112233",
            "scope": "PNUMBER",
            "title": "P-nr."
        }
    ),
    (
        "TEXT", "Adressetype",
        {
            "user_key": "TEXT",
            "example": "Fritekst",
            "scope": "TEXT",
            "title": "Fritekst"
        }
    ),
    (
        "Leder", "Ledertyper",
        {
            "user_key": "Leder",
            "title": "Leder"
        }
    ),
    (
        "Lederansvar", "Lederansvar",
        {
            "user_key": "Lederansvar",
            "title": "Ansvar for organisationsenheden"
        }
    ),
    (
        "Lederniveau", "Lederniveau",
        {
            "user_key": "Lederniveau",
            "title": "Niveau 90",
        }
    ),
    (
        "Ansat", "Engagementstype",
        {
            "user_key": "Ansat",
            "title": "Ansat"
        }
    ),
    (
        "Medarbejder", "Stillingsbetegnelse",
        {
            "user_key": "Generisk Medarbejder",
            "title": "Generisk Medarbejder"
        }
    ),
]
