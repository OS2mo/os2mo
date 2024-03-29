# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from .oio_base import OIORestObject
from .oio_base import OIOStandardHierarchy


class Facet(OIORestObject):
    """
    Implement a Facet  - manage access to database layer from the API.
    """

    pass


class Klasse(OIORestObject):
    """
    Implement a Klasse  - manage access to database layer from the API.
    """

    pass


class Klassifikation(OIORestObject):
    """
    Implement a Klassifikation  - manage access to database from the API.
    """

    pass


class KlassifikationsHierarki(OIOStandardHierarchy):
    """Implement the Klassifikation Standard."""

    _name = "Klassifikation"
    _classes = [Facet, Klasse, Klassifikation]
