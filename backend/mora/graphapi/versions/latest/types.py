# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import json
from base64 import b64decode
from base64 import b64encode
from hashlib import shake_128
from textwrap import dedent

import strawberry
from pydantic.v1 import BaseModel

from mora.util import CPR

# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
    description=dedent(
        """\
        Scalar implementing the danish national identification number / civil registration number.

        The number is a unique identifier for a single individual, although individuals may go through several numbers over time.

        The number is expected to have 10 digits, 6 digits defining a date, and a 4 digit serial number.
        The number does not have to fulfill the modulo 11 checksum.
        It does however (optionally) have to define a valid date.
        No dash should be included to separate the date and serial number sections.

        For further details refer to the Central Person Register (CPR) at:
        * https://cpr.dk/

        Or "Bekendtgørelse af lov om Det Centrale Personregister" ("CPR-Loven"):
        * https://www.retsinformation.dk/eli/lta/2017/646

        Examples:
        * `"0106875049"`
        * `"0106878994"`
        * `"406568970"`
        """
    ),
)


_CURSOR_DELIMITER = ":"


class _Cursor(BaseModel):
    offset: int
    registration_time: datetime.datetime


def _serialize(value: _Cursor) -> str:
    json_bytes = value.json().encode("ascii")
    # This is a hash of the content, rendered as a 6-long hex string. Seems
    # odd, but people like to inspect the cursor while developing to see that
    # pagination actually works. This should make sure that the cursor always
    # looks different, but also that it is actually the same if pagination (or
    # client-side code...) is broken.
    h = shake_128(json_bytes).hexdigest(3)
    cursor = b64encode(json_bytes).decode("ascii")
    return f"{h}{_CURSOR_DELIMITER}{cursor}"


def _deserialize(opaque_cursor: str) -> _Cursor:
    without_hash = opaque_cursor.split(_CURSOR_DELIMITER)[1]
    return _Cursor(**json.loads(b64decode(without_hash)))


Cursor = strawberry.scalar(
    _Cursor,
    serialize=_serialize,
    parse_value=_deserialize,
    description=dedent(
        """\
        Scalar implementing the cursor of cursor-based pagination.

        The cursor is opaque by design abstracting away the underlying implementation details.

        Examples:
        * `"Njk="`
        * `"NDIw"`
        * `"MTMzNw=="`

        Note:

        As the cursor is to be considered opaque its implementation may change in the future.
        I.e. in the future it may be implemented as a simple integer or a complex object.

        The caller should not concern themselves with the actual value contained within, but rather simply pass whatever is returned in the `cursor` argument to continue iteration.
        """
    ),
)
