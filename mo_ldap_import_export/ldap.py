# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""
import datetime
import signal
import time
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from threading import Thread
from typing import Any
from typing import Callable
from typing import cast
from typing import ContextManager
from typing import Dict
from typing import Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastramqpi.context import Context
from ldap3 import Connection
from ldap3 import NTLM
from ldap3 import RANDOM
from ldap3 import RESTARTABLE
from ldap3 import Server
from ldap3 import ServerPool
from ldap3 import Tls
from ldap3.core.exceptions import LDAPInvalidDnError
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn
from more_itertools import always_iterable
from more_itertools import only
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import ObjectType
from ramqp.mo.models import RequestType

from .config import ServerConfig
from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .exceptions import TimeOutException
from .ldap_classes import LdapObject
from .logging import logger
from .processors import _hide_cpr as hide_cpr
from .utils import combine_dn_strings
from .utils import datetime_to_ldap_timestamp
from .utils import mo_object_is_valid


def construct_server(server_config: ServerConfig) -> Server:
    """Construct an LDAP3 server from settings.

    Args:
        server_config: The settings to construct the server instance from.

    Returns:
        The constructed server instance used for LDAP connections.
    """
    tls_configuration = Tls(
        validate=CERT_NONE if server_config.insecure else CERT_REQUIRED
    )

    host = server_config.host
    logger.info(f"Setting up server to {host}")
    return Server(
        host=server_config.host,
        port=server_config.port,
        use_ssl=server_config.use_ssl,
        tls=tls_configuration,
        connect_timeout=server_config.timeout,
    )


def get_client_strategy():
    return RESTARTABLE


def configure_ldap_connection(settings: Settings) -> ContextManager:
    """Configure an LDAP connection.

    Args:
        settings: The Settings instance to configure our ad connection with.

    Returns:
        ContextManager that can be opened to establish an LDAP connection.
    """

    def alarm_handler(signum, frame):
        raise TimeOutException(
            "Timeout while configuring LDAP connection. Try 'sudo tailscale up'?"
        )

    # Set a timeout alarm
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(max([c.timeout for c in settings.ldap_controllers]))

    servers = list(map(construct_server, settings.ldap_controllers))

    # Pick the next server to use at random, discard non-active servers
    server_pool = ServerPool(servers, RANDOM, active=True, exhaust=True)
    client_strategy = get_client_strategy()

    logger.info(f"Connecting to {server_pool}")
    logger.info(f"Client strategy: {client_strategy}")
    connection = Connection(
        server=server_pool,
        user=settings.ldap_domain + "\\" + settings.ldap_user,
        password=settings.ldap_password.get_secret_value(),
        authentication=NTLM,
        client_strategy=get_client_strategy(),
        auto_bind=True,
    )

    # Turn off the alarm
    signal.alarm(0)

    return cast(ContextManager, connection)


async def ldap_healthcheck(context: Union[dict, Context]) -> bool:
    """LDAP connection Healthcheck.

    Args:
        context: To lookup ldap_connection in.

    Returns:
        Whether the AMQPSystem is OK.
    """
    ldap_connection = context["user_context"]["ldap_connection"]
    return cast(bool, ldap_connection.bound)


async def poller_healthcheck(context: Union[dict, Context]) -> bool:
    pollers = context["user_context"]["pollers"]
    for poller in pollers:
        if not poller.is_alive():
            return False
    return True


def get_ldap_schema(ldap_connection: Connection):
    return ldap_connection.server.schema


def get_ldap_object_schema(ldap_connection: Connection, ldap_object: str):
    schema = get_ldap_schema(ldap_connection)
    return schema.object_classes[ldap_object]


def get_ldap_superiors(ldap_connection: Connection, root_ldap_object: str):

    superiors = []
    ldap_object: Union[str, None] = root_ldap_object
    while ldap_object is not None:
        object_schema = get_ldap_object_schema(ldap_connection, ldap_object)
        ldap_object = only(always_iterable(object_schema.superior))
        if ldap_object is not None:
            superiors.append(ldap_object)

    return superiors


def get_ldap_attributes(ldap_connection: Connection, root_ldap_object: str):
    """
    ldap_connection : ldap connection object
    ldap_object : ldap class to fetch attributes for. for example "organizationalPerson"
    """

    all_attributes = []
    superiors = get_ldap_superiors(ldap_connection, root_ldap_object)

    for ldap_object in [root_ldap_object] + superiors:
        object_schema = get_ldap_object_schema(ldap_connection, ldap_object)
        all_attributes += object_schema.may_contain
    return all_attributes


def _paged_search(
    context: Context,
    searchParameters: dict,
    search_base: str,
) -> list:
    """
    searchParameters : dict
        Dict with the following keys:
            * search_filter
            * attributes
    """
    responses = []
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]

    # TODO: Find max. paged_size number from LDAP rather than hard-code it?
    searchParameters["paged_size"] = 500
    searchParameters["search_base"] = search_base

    search_filter = searchParameters["search_filter"]

    logger.info(f"searching for {search_filter} on {search_base}")

    # Max 10_000 pages to avoid eternal loops
    for page in range(0, 10_000):
        logger.info(f"searching page {page}")
        ldap_connection.search(**searchParameters)

        if ldap_connection.result["description"] == "operationsError":
            logger.warn(f"{search_filter} Search failed")
            logger.warn(ldap_connection.result)
            break

        entries = [r for r in ldap_connection.response if r["type"] == "searchResEntry"]
        responses.extend(entries)

        try:
            # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
            extension = "1.2.840.113556.1.4.319"
            cookie = ldap_connection.result["controls"][extension]["value"]["cookie"]
        except KeyError:
            break

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    return responses


def paged_search(
    context: Context,
    searchParameters: dict,
    search_base: Union[str, None] = None,
) -> list:

    if search_base:
        # If the search base is explicitly defined: Don't try anything fancy.
        results = _paged_search(context, searchParameters, search_base)
    else:
        # Otherwise, loop over all OUs to search in
        settings = context["user_context"]["settings"]

        results = []
        for ou in settings.ldap_ous_to_search_in:
            search_base = combine_dn_strings([ou, settings.ldap_search_base])
            results.extend(_paged_search(context, searchParameters, search_base))

    return results


def single_object_search(searchParameters, ldap_connection, exact_dn_match=False):
    """
    Performs an LDAP search and throws an exception if there are multiple or no search
    results.

    Parameters
    -------------
    searchParameters : dict
        Dict with the following keys:
            * search_base
            * search_filter
            * attributes
            * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys

    Notes
    ------
    If you want to be 100% sure that the search only returns one result; Supply an
    object's dn (distinguished name) as the search base and set
    searchFilter = "(objectclass=*)"
    """
    if type(searchParameters["search_base"]) is list:
        search_bases = searchParameters["search_base"].copy()
        modified_searchParameters = searchParameters.copy()
        response = []
        for search_base in search_bases:
            modified_searchParameters["search_base"] = search_base
            ldap_connection.search(**modified_searchParameters)
            response.extend(ldap_connection.response)
    else:
        ldap_connection.search(**searchParameters)
        response = ldap_connection.response

    search_entries = [r for r in response if r["type"] == "searchResEntry"]

    if exact_dn_match:
        search_entries = [
            s for s in search_entries if s["dn"] == searchParameters["search_base"]
        ]

    if len(search_entries) > 1:
        logger.info(response)
        raise MultipleObjectsReturnedException(
            hide_cpr(f"Found multiple entries for {searchParameters}: {search_entries}")
        )
    elif len(search_entries) == 0:
        logger.info(response)
        raise NoObjectsReturnedException(
            hide_cpr(f"Found no entries for {searchParameters}")
        )
    else:
        return search_entries[0]


def is_dn(value):
    """
    Determine if a value is a dn (distinguished name) string
    """
    if type(value) is not str:
        return False

    try:
        safe_dn(value)
        parse_dn(value)
    except LDAPInvalidDnError:
        return False
    else:
        return True


def get_ldap_object(dn, context, nest=True):
    """
    Gets a ldap object based on its DN

    if nest is True, also gets ldap objects of related objects.
    """
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]

    searchParameters = {
        "search_base": dn,
        "search_filter": "(objectclass=*)",
        "attributes": ["*"],
    }
    search_result = single_object_search(
        searchParameters, ldap_connection, exact_dn_match=True
    )
    dn = search_result["dn"]
    logger.info(f"[get_ldap_object] Found {dn}")
    return make_ldap_object(search_result, context, nest=nest)


def make_ldap_object(response: dict, context: Context, nest=True) -> Any:
    """
    Takes an ldap response and formats it as a class

    if nest is True, also makes ldap objects of related objects.
    """
    attributes = sorted(list(response["attributes"].keys()))
    ldap_dict = {"dn": response["dn"]}

    def get_nested_ldap_object(dn):
        """
        Gets a ldap object based on its DN - unless we are in a nested loop
        """

        if nest:
            logger.info(f"[make_ldap_object] Loading nested ldap object with dn={dn}")
            return get_ldap_object(dn, context, nest=False)
        else:  # pragma: no cover
            raise Exception("Already running in nested loop")

    def is_other_dn(value):
        """
        Determine if the value is a dn (distinguished name)
        But not the dn of the main object itself

        This is to avoid that the code requests information about itself
        """
        return is_dn(value) and value != response["dn"]

    for attribute in attributes:
        value = response["attributes"][attribute]
        if is_other_dn(value) and nest:
            ldap_dict[attribute] = get_nested_ldap_object(value)
        elif type(value) is list:
            ldap_dict[attribute] = [
                get_nested_ldap_object(v) if is_other_dn(v) and nest else v
                for v in value
            ]
        else:
            ldap_dict[attribute] = value

    return LdapObject(**ldap_dict)


def get_attribute_types(ldap_connection):
    """
    Returns a dictionary with attribute type information for all attributes in LDAP
    """
    return ldap_connection.server.schema.attribute_types


async def cleanup(
    json_key: str,
    mo_dict_key: str,
    mo_objects: list[Any],
    user_context: dict,
    employee: Employee,
    object_type: ObjectType,
    dn: str,
):
    """
    Cleans entries from LDAP

    json_key : str
        json key to clean for
    value_key : str
        name of the MO attribute that contains the value to be cleaned
    mo_dict_key : str
        name of the key in the conversion dict. i.e. 'mo_employee'
        or 'mo_employee_address'
    mo_objects: list
        List of objects already in MO
    user_context : dict
        user context dictionary with the configured dataloader and converter
    """
    dataloader = user_context["dataloader"]
    converter = user_context["converter"]
    internal_amqpsystem = user_context["internal_amqpsystem"]
    uuids_to_publish = []

    if not converter.__export_to_ldap__(json_key):
        logger.info(f"__export_to_ldap__ == False for json_key = '{json_key}'")
        return

    # Get matching LDAP object for this user (note that LDAP can contain
    # multiple entries in one object)
    attributes = converter.get_ldap_attributes(json_key)
    ldap_object = dataloader.load_ldap_object(dn, attributes)

    logger.info(f"Found the following data in LDAP: {ldap_object}")

    mo_objects = [m for m in mo_objects if mo_object_is_valid(m)]

    # Convert to LDAP-style to make mo-data comparable to LDAP data.
    converted_mo_objects = [
        converter.to_ldap(
            {
                "mo_employee": employee,
                mo_dict_key: mo_object,
            },
            json_key,
            dn,
        )
        for mo_object in mo_objects
    ]
    logger.info(f"Found the following data in MO: {converted_mo_objects}")

    # Loop over each attribute and determine if it needs to be cleaned
    ldap_objects_to_clean = []
    for attribute in attributes:
        values_in_ldap = getattr(ldap_object, attribute)
        values_in_mo: list[Any] = list(
            filter(None, [getattr(o, attribute, None) for o in converted_mo_objects])
        )

        if type(values_in_ldap) is not list:
            values_in_ldap = [values_in_ldap] if values_in_ldap else []

        # If a value is in LDAP but NOT in MO, it needs to be cleaned
        for value_in_ldap in values_in_ldap:
            if value_in_ldap not in values_in_mo:
                logger.info(f"{attribute} = '{value_in_ldap}' needs cleaning")
                ldap_objects_to_clean.append(
                    LdapObject(**{"dn": dn, attribute: value_in_ldap})
                )

        # If MO contains values and LDAP doesn't, send AMQP messages to export to LDAP
        # This can happen, if we delete an address in MO, and another address already
        # exists in MO. In that case the other address should be written to LDAP,
        # after the first one is deleted from LDAP
        if not values_in_ldap and values_in_mo:
            logger.info(f"attribute = '{attribute}' needs to be written to LDAP")
            uuids_to_publish = [o.uuid for o in mo_objects]

    # Clean from LDAP
    if len(ldap_objects_to_clean) == 0:
        logger.info("No synchronization required")
    else:
        dataloader.cleanup_attributes_in_ldap(ldap_objects_to_clean)

    # Publish to internal AMQP system
    for uuid in uuids_to_publish:
        mo_object_dict = await dataloader.load_mo_object(str(uuid), object_type)
        routing_key = MORoutingKey.build(
            service_type=mo_object_dict["service_type"],
            object_type=mo_object_dict["object_type"],
            request_type=RequestType.REFRESH,
        )
        payload = mo_object_dict["payload"]

        logger.info(f"Publishing {routing_key}")
        logger.info(f"with payload.uuid = {payload.uuid}")
        logger.info(f"and payload.object_uuid = {payload.object_uuid}")

        await internal_amqpsystem.publish_message(
            str(routing_key), jsonable_encoder(payload)
        )


def setup_listener(context: Context, callback: Callable) -> list[Thread]:
    user_context = context["user_context"]

    # Note:
    # We need the dn attribute to trigger sync_tool.import_single_user()
    # We need the modifyTimeStamp attribute to check for duplicate events in _poller()
    settings = user_context["settings"]
    pollers = []
    for ldap_ou_to_scan_for_changes in settings.ldap_ous_to_search_in:
        search_base = combine_dn_strings(
            [ldap_ou_to_scan_for_changes, settings.ldap_search_base]
        )

        search_parameters = {
            "search_base": search_base,
            "search_filter": "(cn=*)",
            "attributes": ["distinguishedName", "modifyTimestamp"],
        }

        # Polling search
        pollers.append(
            setup_poller(
                context,
                callback,
                search_parameters,
                datetime.datetime.utcnow(),
                user_context["poll_time"],
            )
        )
    return pollers


def setup_poller(
    context: Context,
    callback: Callable,
    search_parameters: dict,
    init_search_time: datetime.datetime,
    poll_time: float,
) -> Thread:
    poll = Thread(
        target=_poller,
        args=(
            context["user_context"]["ldap_connection"],
            search_parameters,
            callback,
            init_search_time,
            poll_time,
        ),
        daemon=True,
    )
    poll.start()
    return poll


def _poller(
    ldap_connection: Connection,
    search_parameters: dict,
    callback: Callable,
    init_search_time: datetime.datetime,
    poll_time: float,
) -> None:
    """
    Method to run in a thread that polls the LDAP server every poll_time seconds,
    with a search that includes the timestamp for the last search
    and calls the `callback` for each result found
    """
    last_search_time = init_search_time
    last_events: list[Any] = []

    while True:
        time.sleep(poll_time)
        logger.debug(f"Searching for changes since {last_search_time}")
        timed_search_parameters = set_search_params_modify_timestamp(
            search_parameters,
            last_search_time,
        )
        last_search_time = datetime.datetime.utcnow()
        ldap_connection.search(**timed_search_parameters)

        events_to_ignore = last_events.copy()
        last_events = []

        if ldap_connection.response:
            for event in ldap_connection.response:
                if event.get("type") == "searchResEntry":

                    # We require modifyTimeStamp to determine if the event is duplicate
                    if "modifyTimeStamp" not in event.get("attributes", {}):
                        logger.warning(
                            "'modifyTimeStamp' not found in event['attributes']"
                        )
                    else:
                        if event not in events_to_ignore:
                            callback(event)
                            last_events.append(event)
                        else:
                            # Some events get detected twice, because LDAP's >= filter
                            # does not quite work with millisecond precision.
                            #
                            # For example: When modifyTimeStamp == 20230307120826.0Z:
                            # We get a hit for the following search filters:
                            # - (modifyTimestamp>=20230307120825.256-0000)
                            # - (modifyTimestamp>=20230307120826.341-0000)
                            #
                            # Even though you would expect the second one not to match
                            logger.info(f"Ignored duplicate event: {event}")


def set_search_params_modify_timestamp(
    search_parameters: Dict, timestamp: datetime.datetime
):
    changed_str = f"(modifyTimestamp>={datetime_to_ldap_timestamp(timestamp)})"
    search_filter = search_parameters["search_filter"]
    if not search_filter.startswith("(") or not search_filter.endswith(")"):
        search_filter = f"({search_filter})"
    return {
        **search_parameters,
        "search_filter": "(&" + changed_str + search_filter + ")",
    }


def is_guid(objectGUID: Any):
    """
    Check if a string is a valid UUID
    """
    if type(objectGUID) is UUID:
        return True
    elif type(objectGUID) is not str:
        return False
    else:
        try:
            UUID(objectGUID)
            return True
        except Exception:
            return False
