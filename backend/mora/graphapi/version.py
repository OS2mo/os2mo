# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from typing import Any


@enum.unique
class Version(enum.Enum):
    """Available GraphQL Schema versions.

    We do not use `Version(int, Enum)` or `Version(IntEnum)` to disallow
    comparison with primitive integers. Forcing the use of `Version.VERSION_N`
    enables better type-checking and discoverability for developers using
    go-to-definition/references.
    """

    VERSION_18 = 18
    VERSION_19 = 19
    VERSION_20 = 20
    VERSION_21 = 21
    VERSION_22 = 22
    VERSION_23 = 23
    VERSION_24 = 24
    VERSION_25 = 25
    VERSION_26 = 26
    VERSION_27 = 27
    VERSION_28 = 28

    # Define __ge__, __gt__, __le__, and __lt__ to allow comparison of versions
    # despite not being an IntEnum.
    # https://docs.python.org/3/howto/enum.html#orderedenum

    def __ge__(self, other: Any) -> bool:
        if self.__class__ is not other.__class__:  # pragma: no cover
            return NotImplemented
        return self.value >= other.value

    def __gt__(self, other: Any) -> bool:
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.value > other.value

    def __le__(self, other: Any) -> bool:
        if self.__class__ is not other.__class__:  # pragma: no cover
            return NotImplemented
        return self.value <= other.value

    def __lt__(self, other: Any) -> bool:  # pragma: no cover
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.value < other.value


LATEST_VERSION = max(Version)
