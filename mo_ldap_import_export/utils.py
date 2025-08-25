# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import datetime
from datetime import time
from functools import partial
from functools import wraps
from typing import Any
from typing import TypeVar
from typing import cast
from zoneinfo import ZoneInfo

import structlog
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn

from .models import Address
from .models import Class
from .models import Employee
from .models import Engagement
from .models import ITSystem
from .models import ITUser
from .models import JobTitleFromADToMO
from .models import MOBase
from .models import OrganisationUnit
from .types import DN
from .types import RDN

logger = structlog.stdlib.get_logger()

T = TypeVar("T")
R = TypeVar("R")

MO_TZ = ZoneInfo("Europe/Copenhagen")


def mo_today() -> datetime:
    """MO does not support datetimes with a time, haha."""
    now = datetime.now(tz=MO_TZ)
    return datetime.combine(now, time.min, now.tzinfo)


def import_class(name: str) -> type[MOBase]:
    import_map: dict[str, type[MOBase]] = {
        "Custom.JobTitleFromADToMO": JobTitleFromADToMO,
        "Address": Address,
        "Engagement": Engagement,
        "ITUser": ITUser,
        "ITSystem": ITSystem,
        "Class": Class,
        "Employee": Employee,
        "OrganisationUnit": OrganisationUnit,
    }
    clazz = import_map.get(name)
    if clazz is None:
        raise NotImplementedError("Unknown argument to import_class")
    return clazz


# TODO: this doesn't work in any possible definition of the word "work". Delete
# as soon as we pass GraphQL objects around.
def mo_datestring_to_utc(datestring: str | None) -> datetime | None:
    """
    Returns datetime object at UTC+0

    Notes
    ------
    Mo datestrings are formatted like this: "2023-02-27T00:00:00+01:00"
    This function essentially removes the "+01:00" part, which gives a UTC+0 timestamp.
    """
    if datestring is None:
        return None
    return datetime.fromisoformat(datestring).replace(tzinfo=None)


def combine_dn_strings(rdns: list[RDN]) -> DN:
    """Combine LDAP RDN strings, skipping empty RDNs.

    Examples:
        >>> combine_dn_strings(["CN=Nick","","DC=bar"])
        >>> "CN=Nick,DC=bar"

    Args:
        rdns: List of potentially empty RDNs to be combined.

    Returns:
        The combined DN after removed empty RDNs.
    """
    dn_strings = [rdn for rdn in rdns if rdn]
    return cast(DN, safe_dn(dn_strings))


def remove_vowels(string: str) -> str:
    return re.sub("[aeiouAEIOU]", "", string)


def extract_part_from_dn(dn: DN, index_string: str) -> str:
    """
    Extract a part from an LDAP DN string

    Examples
    -------------
    >>> extract_part_from_dn("CN=Tobias,OU=mucki,OU=bar,DC=k","OU")
    >>> "OU=mucki,OU=bar"
    """
    parts = [
        f"{attribute_type}={attribute_value}"
        for attribute_type, attribute_value, separator in parse_dn(dn)
        if attribute_type.lower() == index_string.lower()
    ]
    if not parts:
        return ""
    return cast(str, safe_dn(parts))


extract_ou_from_dn = partial(extract_part_from_dn, index_string="OU")


def is_list(x: Any | list[Any]) -> bool:
    """Decide whether the provided argument is a list.

    Args:
        x: A potential list.

    Returns:
        Whether the provided argument is a list or not.
    """
    return isinstance(x, list)


def is_exception(x: Any) -> bool:
    """Decide whether the provided argument is an exception.

    Args:
        x: A potential exception.

    Returns:
        Whether the provided argument is an exception or not.
    """
    return isinstance(x, Exception)


def ensure_list(x: Any | list[Any]) -> list[Any]:
    """Wrap the argument in a list if not a list.

    Args:
        x: A potential list.

    Returns:
        The provided argument unmodified, if a list.
        The provided argument wrapped in a list, if not a list.
    """
    if is_list(x):
        return x
    return [x]


# TODO: Refactor this to use structured object
def get_delete_flag(mo_object: dict[str, Any]) -> bool:
    """Determines if an object should be deleted based on the validity to-date.

    Args:
        mo_object: The object to test.

    Returns:
        Whether the object should be deleted or not.
    """
    # TODO: use timezone-aware datetime for now. GraphQL objects are already
    # timezone-aware, so we can delete all parsing logic from here when we rid
    # ourselves of the ramodels infestation.
    now = datetime.utcnow()
    validity_to = mo_datestring_to_utc(mo_object["validity"]["to"])
    if validity_to and validity_to <= now:
        logger.info(
            "Returning delete=True because to_date <= current_date",
            to_date=validity_to,
            current_date=now,
        )
        return True
    return False


def star(func):
    @wraps(func)
    def wrapper(tup: tuple) -> Any:
        return func(*tup)

    return wrapper
