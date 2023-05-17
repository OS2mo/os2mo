# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
import asyncio
import copy
import datetime
import re
from typing import Union

from gql import gql
from graphql import DocumentNode
from graphql import print_ast
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn
from ldap3.utils.dn import to_dn

from .exceptions import InvalidQuery
from .logging import logger


# https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
def import_class(name):
    components = name.split(".")
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# https://stackoverflow.com/questions/3405715/elegant-way-to-remove-fields-from-nested-dictionaries
def _delete_keys_from_dict(dict_del, lst_keys):
    for field in list(dict_del.keys()):
        if field in lst_keys:
            del dict_del[field]
        elif type(dict_del[field]) is dict:
            _delete_keys_from_dict(dict_del[field], lst_keys)
    return dict_del


def delete_keys_from_dict(dict_del, lst_keys):
    """
    Delete the keys present in lst_keys from the dictionary.
    Loops recursively over nested dictionaries.
    """
    return _delete_keys_from_dict(copy.deepcopy(dict_del), lst_keys)


def add_filter_to_query(query: DocumentNode, filter_to_add: str) -> DocumentNode:
    """
    Attempts to modify a query with an additional filter.

    Parameters
    -------------
    query : gql document node
        The query to modify
    filter_to_add : str
        The filter(s) to add to the query. For example "to_date: null, from_date: null"

    Notes
    ------
    When from_date and to_date equal "null", all objects are returned, rather than just
    objects which are valid now. That means that future and past object are returned
    as well as current ones.
    """
    query_str = print_ast(query)

    try:
        index = query_str.index(")")  # Raises ValueError if substring is not found
        new_query_str = query_str[0:index] + ", " + filter_to_add + query_str[index:]
    except ValueError:
        raise InvalidQuery(
            (
                f"Could not modify query filters for '{query_str}'. "
                "Looks like the query has no filters"
            )
        )

    logger.info(f"Modified '{query_str}' to '{new_query_str}'")
    return gql(new_query_str)


def mo_datestring_to_utc(datestring: Union[str, None]):
    """
    Returns datetime object at UTC+0

    Notes
    ------
    Mo datestrings are formatted like this: "2023-02-27T00:00:00+01:00"
    This function essentially removes the "+01:00" part, which gives a UTC+0 timestamp.
    """
    if datestring:
        return datetime.datetime.fromisoformat(datestring).replace(tzinfo=None)
    else:
        return None


def mo_object_is_valid(mo_object):
    now = datetime.datetime.utcnow()

    if mo_object.validity.to_date is None:
        return True
    elif mo_object.validity.to_date.replace(tzinfo=None) > now:
        return True
    else:
        return False


def datetime_to_ldap_timestamp(dt: datetime.datetime):
    return "".join(
        [
            dt.strftime("%Y%m%d%H%M%S"),
            ".",
            str(int(dt.microsecond / 1000)),
            (dt.strftime("%z") or "-0000"),
        ]
    )


def listener(context, event):
    """
    Calls import_single_user if changes are registered
    """

    user_context = context["user_context"]
    event_loop = user_context["event_loop"]
    sync_tool = user_context["sync_tool"]

    dn = event.get("attributes", {}).get("distinguishedName", None)

    if dn:
        logger.info(f"Registered change for LDAP object with dn={dn}")
        event_loop.create_task(sync_tool.import_single_user(dn))
    else:
        logger.info(f"Got event without dn: {event}")


async def countdown(
    seconds_to_sleep: float,
    task_description: str,
    update_interval: float = 60,
):
    """
    Sleep for 'seconds_to_sleep' seconds.
    Print an update every 'update_interval' seconds

    Note: We use asyncio.sleep because it is non-blocking
    """
    seconds_remaining = seconds_to_sleep
    while seconds_remaining > 0:
        minutes, seconds = divmod(seconds_remaining, 60)
        hours, minutes = divmod(minutes, 60)
        logger.info(
            (
                f"Starting {task_description} in "
                f"{hours} hours, {minutes} min, {seconds} sec"
            )
        )
        await asyncio.sleep(min(update_interval, seconds_remaining))
        seconds_remaining -= update_interval


def combine_dn_strings(dn_strings: list[str]) -> str:
    """
    Combine LDAP DN strings, skipping if a string is empty

    Examples
    ---------------
    >>> combine_dn_strings(["CN=Nick","","DC=bar"])
    >>> "CN=Nick,DC=bar"
    """
    lst: list[str] = list(
        filter(
            None,
            dn_strings,
        )
    )
    dn: str = safe_dn(",".join(lst))
    return dn


def remove_vowels(string):
    return re.sub("[aeiouAEIOU]", "", string)


def extract_ou_from_dn(dn: str) -> str:
    """
    Extract the OU part from an LDAP DN string

    Examples
    -------------
    >>> extract_ou_from_dn("CN=Tobias,OU=mucki,OU=bar,DC=k")
    >>> "OU=mucki,OU=bar"
    """
    dn_parts = to_dn(dn)
    ou_parts = []
    for dn_part in dn_parts:
        dn_decomposed = parse_dn(dn_part)[0]
        if dn_decomposed[0].lower() == "ou":
            ou_parts.append(dn_part)

    if ou_parts:
        ou: str = safe_dn(",".join(ou_parts))
        return ou
    else:
        return ""
