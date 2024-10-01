# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import string
from datetime import datetime
from functools import partial
from typing import Any
from uuid import uuid4

from jinja2 import Environment  # noqa: E402
from jinja2 import Undefined

from .config import Settings
from .dataloaders import DataLoader


def filter_mo_datestring(datetime_object):
    """
    Converts a datetime object to a date string which is accepted by MO.

    Notes
    -------
    MO only accepts date objects dated at midnight.
    """
    # TODO: should take timezone-aware datetime_object and convert using MO_TZ.
    if not datetime_object:
        return None
    return datetime_object.strftime("%Y-%m-%dT00:00:00")


def filter_strip_non_digits(input_string):
    if not isinstance(input_string, str):
        return None
    return "".join(c for c in input_string if c in string.digits)


def filter_splitfirst(text, separator=" "):
    """
    Splits a string at the first space, returning two elements
    This is convenient for splitting a name into a givenName and a surname
    and works for names with no spaces (surname will then be empty)
    """
    if text is not None:
        text = str(text)
        if text != "":
            s = text.split(separator, 1)
            return s if len(s) > 1 else (s + [""])
    return ["", ""]


def filter_splitlast(text, separator=" "):
    """
    Splits a string at the last space, returning two elements
    This is convenient for splitting a name into a givenName and a surname
    and works for names with no spaces (givenname will then be empty)
    """
    if text is not None:
        text = str(text)
        if text != "":
            text = str(text)
            s = text.split(separator)
            return [separator.join(s[:-1]), s[-1]]
    return ["", ""]


def filter_remove_curly_brackets(text: str) -> str:
    # TODO: Should this remove everything or just a single set?
    return text.replace("{", "").replace("}", "")


def bitwise_and(input: int, bitmask: int) -> int:
    """Bitwise and jinja filter.

    Mostly useful for accessing bits within userAccountControl.

    Args:
        input: The input integer.
        bitmask: The bitmask to filter the input through.

    Returns:
        The bitwise and on input and bitmask.
    """
    return input & bitmask


def minimum(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def nonejoin(*args) -> str:
    """
    Joins items together if they are not None or empty lists
    """
    items_to_join = [a for a in args if a]
    return ", ".join(items_to_join)


def nonejoin_orgs(org_unit_path_string_separator: str, *args) -> str:
    """
    Joins orgs together if they are not empty strings
    """
    sep = org_unit_path_string_separator

    items_to_join = [a.strip() for a in args if a]
    return sep.join(items_to_join)


def remove_first_org(org_unit_path_string_separator: str, orgstr: str) -> str:
    """
    Remove first org from orgstr
    """
    sep = org_unit_path_string_separator

    _, *rest = orgstr.split(sep)
    return nonejoin_orgs(sep, *rest)


def construct_globals_dict(
    settings: Settings, dataloader: DataLoader
) -> dict[str, Any]:
    from .converters import get_current_engagement_type_uuid_dict
    from .converters import get_current_org_unit_uuid_dict
    from .converters import get_current_primary_uuid_dict
    from .converters import get_employee_address_type_uuid
    from .converters import get_employee_dict
    from .converters import get_engagement_type_name
    from .converters import get_engagement_type_uuid
    from .converters import get_it_system_uuid
    from .converters import get_job_function_name
    from .converters import get_job_function_uuid
    from .converters import get_or_create_engagement_type_uuid
    from .converters import get_or_create_job_function_uuid
    from .converters import get_or_create_org_unit_uuid
    from .converters import get_org_unit_address_type_uuid
    from .converters import get_org_unit_name
    from .converters import get_org_unit_name_for_parent
    from .converters import get_org_unit_path_string
    from .converters import get_primary_engagement_dict
    from .converters import get_primary_type_uuid
    from .converters import get_visibility_uuid
    from .converters import make_dn_from_org_unit_path
    from .converters import org_unit_path_string_from_dn

    return {
        "now": datetime.utcnow,  # TODO: timezone-aware datetime
        "min": minimum,
        "nonejoin": nonejoin,
        "nonejoin_orgs": partial(
            nonejoin_orgs, settings.org_unit_path_string_separator
        ),
        "remove_first_org": partial(
            remove_first_org, settings.org_unit_path_string_separator
        ),
        "get_employee_address_type_uuid": partial(
            get_employee_address_type_uuid, dataloader.graphql_client
        ),
        "get_org_unit_address_type_uuid": partial(
            get_org_unit_address_type_uuid, dataloader.graphql_client
        ),
        "get_it_system_uuid": partial(get_it_system_uuid, dataloader.graphql_client),
        "get_or_create_org_unit_uuid": partial(
            get_or_create_org_unit_uuid, dataloader, settings
        ),
        "org_unit_path_string_from_dn": partial(
            org_unit_path_string_from_dn,
            settings.org_unit_path_string_separator,
        ),
        "get_job_function_uuid": partial(
            get_job_function_uuid, dataloader.graphql_client
        ),
        "get_visibility_uuid": partial(get_visibility_uuid, dataloader.graphql_client),
        "get_primary_type_uuid": partial(
            get_primary_type_uuid, dataloader.graphql_client
        ),
        "get_engagement_type_uuid": partial(
            get_engagement_type_uuid, dataloader.graphql_client
        ),
        "get_engagement_type_name": partial(
            get_engagement_type_name, dataloader.graphql_client
        ),
        "uuid4": uuid4,
        "get_org_unit_path_string": partial(
            get_org_unit_path_string,
            dataloader.graphql_client,
            settings.org_unit_path_string_separator,
        ),
        "get_org_unit_name_for_parent": partial(
            get_org_unit_name_for_parent, dataloader.graphql_client
        ),
        "make_dn_from_org_unit_path": partial(
            make_dn_from_org_unit_path, settings.org_unit_path_string_separator
        ),
        "get_job_function_name": partial(
            get_job_function_name, dataloader.graphql_client
        ),
        "get_org_unit_name": partial(get_org_unit_name, dataloader.graphql_client),
        "get_or_create_job_function_uuid": partial(
            get_or_create_job_function_uuid, dataloader
        ),
        "get_or_create_engagement_type_uuid": partial(
            get_or_create_engagement_type_uuid, dataloader
        ),
        "get_current_org_unit_uuid_dict": partial(
            get_current_org_unit_uuid_dict, dataloader
        ),
        "get_current_engagement_type_uuid_dict": partial(
            get_current_engagement_type_uuid_dict, dataloader
        ),
        "get_current_primary_uuid_dict": partial(
            get_current_primary_uuid_dict, dataloader
        ),
        "get_primary_engagement_dict": partial(get_primary_engagement_dict, dataloader),
        "get_employee_dict": partial(get_employee_dict, dataloader),
    }


def construct_environment(settings: Settings, dataloader: DataLoader) -> Environment:
    environment = Environment(undefined=Undefined, enable_async=True)

    environment.filters["bitwise_and"] = bitwise_and
    environment.filters["splitfirst"] = filter_splitfirst
    environment.filters["splitlast"] = filter_splitlast
    environment.filters["mo_datestring"] = filter_mo_datestring
    environment.filters["strip_non_digits"] = filter_strip_non_digits
    environment.filters["remove_curly_brackets"] = filter_remove_curly_brackets

    environment.globals.update(construct_globals_dict(settings, dataloader))

    return environment
