# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic import parse_obj_as

from mora import util
from mora.service.address_handler.email import EmailAddressHandler

UUID_SEARCH_MIN_PHRASE_LENGTH = 7


def string_to_urn(urn_string: str) -> str:
    if util.is_uuid(urn_string):  # pragma: no cover
        return urn_string

    # EMAIL urn handling
    try:
        parse_obj_as(EmailStr, urn_string)
        return EmailAddressHandler(value=urn_string, visibility=None).urn
    except ValidationError:
        pass

    # Default/fallback urn handling
    return util.urnquote(urn_string)
