# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ._shared import LoraBase
from .facet import Facet
from .facet import FacetRead
from .itsystem import ITSystem
from .klasse import Klasse
from .klasse import KlasseRead
from .organisation import Organisation
from .organisation import OrganisationRead

__all__ = [
    "LoraBase",
    "Facet",
    "FacetRead",
    "Klasse",
    "KlasseRead",
    "Organisation",
    "OrganisationRead",
    "ITSystem",
]
