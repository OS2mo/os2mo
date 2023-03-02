# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
import copy
import datetime

import structlog
from gql import gql
from graphql import DocumentNode
from graphql import print_ast

from .exceptions import InvalidQuery


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
    logger = structlog.get_logger()
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


def mo_datestring_to_utc(datestring: str):
    """
    Returns datetime object at UTC+0

    Notes
    ------
    Mo datestrings are formatted like this: "2023-02-27T00:00:00+01:00"
    This function essentially removes the "+01:00" part, which gives a UTC+0 timestamp.
    """
    return datetime.datetime.fromisoformat(datestring).replace(tzinfo=None)


def mo_object_is_valid(mo_object):
    now = datetime.datetime.utcnow()

    if mo_object.validity.to_date is None:
        return True
    elif mo_object.validity.to_date.replace(tzinfo=None) > now:
        return True
    else:
        return False
