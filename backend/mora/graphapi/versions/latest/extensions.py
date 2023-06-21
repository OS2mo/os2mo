# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# Extension
# -----
from textwrap import dedent

import strawberry

from ramodels.mo import ExtensionsField as ExtensionFieldModel


@strawberry.experimental.pydantic.type(
    model=ExtensionFieldModel,
    all_fields=True,
    description=dedent(
        """
        A class for allowing arbitrary values in extension fields.

        May be used for extraordinary occasions when no better option of storing data exists.
        """
    ),
)
class ExtensionsField:
    pass
