# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

from mora.graphapi.version import Version


# TODO: use TypedDict with extra_items=Never
# https://peps.python.org/pep-0728/
class Metadata(dict):
    def __init__(self, version: Callable[[Version], bool] | None = None) -> None:
        super().__init__(version=version)
