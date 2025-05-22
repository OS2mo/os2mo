# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""

import asyncio
import signal
from collections import ChainMap
from contextlib import suppress
from functools import cache
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from typing import Any
from typing import Self
from uuid import UUID

import ldap3.core.exceptions
import structlog
from fastramqpi.context import Context
from fastramqpi.ramqp.utils import RequeueMessage
from jinja2 import Template
from ldap3 import ASYNC
from ldap3 import BASE
from ldap3 import NO_ATTRIBUTES
from ldap3 import NTLM
from ldap3 import RANDOM
from ldap3 import SIMPLE
from ldap3 import Connection
from ldap3 import Server
from ldap3 import ServerPool
from ldap3 import Tls
from ldap3 import set_config_parameter
from ldap3.core.exceptions import LDAPInvalidDnError
from ldap3.core.exceptions import LDAPNoSuchObjectResult
from ldap3.operation.search import FilterNode
from ldap3.operation.search import compile_filter
from ldap3.operation.search import parse_filter
from ldap3.protocol.rfc4511 import Filter as RFC4511Filter
from ldap3.utils.conv import escape_filter_chars
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn
from more_itertools import one
from more_itertools import only
from pyasn1.codec.ber import encoder as ber_encoder

from .config import AuthBackendEnum
from .config import ServerConfig
from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .exceptions import TimeOutException
from .ldap_classes import LdapObject
from .types import DN
from .types import RDN
from .utils import combine_dn_strings
from .utils import ensure_list
from .utils import is_list

logger = structlog.stdlib.get_logger()


def construct_server(server_config: ServerConfig) -> Server:
    """Construct an LDAP3 server from settings.

    Args:
        server_config: The settings to construct the server instance from.

    Returns:
        The constructed server instance used for LDAP connections.
    """
    tls_configuration = Tls(
        validate=CERT_NONE if server_config.insecure else CERT_REQUIRED,
        ca_certs_data=server_config.ca_certs_data,
    )

    host = server_config.host
    logger.info("Setting up server", host=host)
    return Server(
        host=server_config.host,
        port=server_config.port,
        use_ssl=server_config.use_ssl,
        tls=tls_configuration,
        connect_timeout=server_config.timeout,
    )


def get_client_strategy():
    # NOTE: We probably want to use REUABLE, but it introduces issues with regards to
    #       presumed lazily fetching of the schema. See the comment in get_ldap_schema.
    return ASYNC


def construct_server_pool(settings: Settings) -> ServerPool:
    servers = list(map(construct_server, settings.ldap_controllers))
    # Pick the next server to use at random, retry connections 10 times,
    # discard non-active servers.
    server_pool = ServerPool(
        servers,
        RANDOM,
        active=10,  # type: ignore[arg-type]
        exhaust=True,
    )
    return server_pool


def configure_ldap_connection(settings: Settings) -> Connection:
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

    server_pool = construct_server_pool(settings)
    client_strategy = get_client_strategy()

    logger.info(
        "Connecting to server",
        server_pool=server_pool,
        client_strategy=client_strategy,
        auth_strategy=settings.ldap_auth_method.value,
    )

    connection_kwargs = {
        "server": server_pool,
        "client_strategy": client_strategy,
        "password": settings.ldap_password.get_secret_value(),
        "auto_bind": True,
        "raise_exceptions": True,
        # Configure non-blocking IO, with maximum time to wait for each reply
        "receive_timeout": settings.ldap_receive_timeout,
        # NOTE: It appears that this flag does not in fact work
        # See: https://github.com/cannatag/ldap3/issues/1008
        "read_only": settings.ldap_read_only,
    }
    set_config_parameter("RESPONSE_WAITING_TIMEOUT", settings.ldap_response_timeout)
    match settings.ldap_auth_method:
        case AuthBackendEnum.NTLM:
            connection_kwargs.update(
                {
                    "user": settings.ldap_domain + "\\" + settings.ldap_user,
                    "authentication": NTLM,
                }
            )
        case AuthBackendEnum.SIMPLE:
            connection_kwargs.update(
                {
                    "user": settings.ldap_user,
                    "authentication": SIMPLE,
                }
            )
        case _:
            # Turn off the alarm
            signal.alarm(0)
            raise ValueError("Unknown authentication backend")

    try:
        connection = Connection(**connection_kwargs)
    except ldap3.core.exceptions.LDAPBindError as exc:
        logger.exception("Exception during LDAP auth")
        raise exc
    finally:
        # Turn off the alarm
        signal.alarm(0)

    return connection


async def ldap_healthcheck(context: dict | Context) -> bool:
    """LDAP connection Healthcheck.

    Args:
        context: To lookup ldap_connection in.

    Returns:
        Whether the LDAP connection is OK.
    """
    logger.debug("Running LDAP healthcheck")
    ldap_connection = context["user_context"]["ldap_connection"]
    if ldap_connection.bound is False:
        logger.warning("LDAP connection not bound")
        return False
    if ldap_connection.listening is False:
        logger.warning("LDAP connection not listening")
        return False
    if ldap_connection.closed is True:
        logger.warning("LDAP connection not open")
        return False
    try:
        # Try to do a 'SELECT 1' like query, selecting the empty DN
        response, result = await ldap_search(
            ldap_connection,
            search_base="",
            search_filter="(objectclass=*)",
            attributes=NO_ATTRIBUTES,
            search_scope=BASE,
            size_limit=1,
        )
    except Exception:
        logger.exception("LDAP connection was unable to search")
        return False
    if result["type"] != "searchResDone":
        logger.warning(
            "LDAP connection search returned unexpected result type",
            response=response,
            result=result,
        )
        return False
    if result["description"] != "success":
        logger.warning(
            "LDAP connection did not search sucessfully",
            response=response,
            result=result,
        )
        return False
    logger.debug("LDAP healthcheck passed", response=response, result=result)
    return True


class LDAPConnection:
    def __init__(self: Self, connection: Connection) -> None:
        self.connection = connection

    async def _wait_for_message_id(self: Self, message_id: int) -> tuple[Any, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.connection.get_response, message_id
        )

    async def ldap_add(
        self: Self, dn: DN, object_class, attributes=None
    ) -> tuple[dict, dict]:
        message_id = self.connection.add(dn, object_class, attributes)
        response, result = await self._wait_for_message_id(message_id)
        return response, result

    async def ldap_modify(
        self: Self,
        dn: DN,
        changes: dict,
        controls: list[tuple[str, bool, Any | None]] | None = None,
    ) -> tuple[dict, dict]:
        message_id = self.connection.modify(dn, changes, controls)
        response, result = await self._wait_for_message_id(message_id)
        return response, result

    async def ldap_modify_dn(
        self: Self,
        dn: DN,
        relative_dn: RDN,
        new_superior: Any | None = None,
    ) -> tuple[dict, dict]:
        message_id = self.connection.modify_dn(
            dn, relative_dn, new_superior=new_superior
        )
        response, result = await self._wait_for_message_id(message_id)
        return response, result

    async def ldap_delete(self: Self, dn: DN) -> tuple[dict, dict]:
        message_id = self.connection.delete(dn)
        response, result = await self._wait_for_message_id(message_id)
        return response, result

    async def ldap_search(self: Self, **kwargs) -> tuple[list[dict[str, Any]], dict]:
        message_id = self.connection.search(**kwargs)
        response, result = await self._wait_for_message_id(message_id)
        return response, result


async def ldap_modify(
    ldap_connection: Connection,
    dn: DN,
    changes: dict,
    controls: list[tuple[str, bool, Any | None]] | None = None,
) -> tuple[dict, dict]:
    connection = LDAPConnection(ldap_connection)
    return await connection.ldap_modify(dn, changes, controls)


async def ldap_modify_dn(
    ldap_connection: Connection,
    dn: DN,
    relative_dn: RDN,
    new_superior: Any | None = None,
) -> tuple[dict, dict]:
    connection = LDAPConnection(ldap_connection)
    return await connection.ldap_modify_dn(dn, relative_dn, new_superior)


async def ldap_add(
    ldap_connection: Connection, dn: DN, object_class, attributes=None
) -> tuple[dict, dict]:
    connection = LDAPConnection(ldap_connection)
    return await connection.ldap_add(dn, object_class, attributes)


async def ldap_search(
    ldap_connection: Connection, **kwargs
) -> tuple[list[dict[str, Any]], dict]:
    connection = LDAPConnection(ldap_connection)
    return await connection.ldap_search(**kwargs)


async def fetch_field_mapping(
    ldap_connection: Connection, discriminator_fields: list[str], dn: DN
) -> dict[str, str | int | None]:
    # Fetch the discriminator attributes for all the given DN
    # NOTE: While it is possible to fetch multiple DNs in a single operation
    #       (by doing a complex search operation), some "guy on the internet" claims
    #       that it is better to lookup DNs individually using the READ operation.
    #       See: https://stackoverflow.com/a/58834059
    try:
        ldap_object = await get_ldap_object(
            ldap_connection, dn, attributes=set(discriminator_fields)
        )
    except NoObjectsReturnedException as exc:
        # There could be multiple reasons why our DNs cannot be read.
        # * The DNs could have been found by CPR number and changed since then.
        #
        # In this case, we wish to retry the message, so we can refetch by CPR.
        #
        # * The DNs could have been found by ITUsers and those could be wrong in MO
        #
        # In this case, we wish to retry the message until someone has fixed the
        # problem in MO itself, and thus we will be retrying for a long time, likely
        # raising an alarm due to messages not being processed, and thus ensuring that
        # someone will look into the issue.
        raise RequeueMessage("Unable to lookup DN(s)") from exc

    def ldapobject2discriminator(
        ldap_object: LdapObject, discriminator_field: str
    ) -> str | int | None:
        # The value can either be a string or a list
        value = getattr(ldap_object, discriminator_field, None)
        if value is None:
            logger.debug(
                "Discriminator value is None before unpacking", dn=ldap_object.dn
            )
            return None
        # TODO: Figure out when it is a string instead of a list
        #       Maybe it is an AD only thing?
        # NOTE: userAccountControl is in integer attribute
        if isinstance(value, str | int):  # pragma: no cover
            return value
        # If it is a list, we assume it is
        unpacked_value = only(value)
        if unpacked_value is None:
            logger.debug("Discriminator value is None", dn=ldap_object.dn)
            return None
        assert isinstance(unpacked_value, str)
        return unpacked_value

    return {
        discriminator_field: ldapobject2discriminator(ldap_object, discriminator_field)
        for discriminator_field in discriminator_fields
    }


async def fetch_dn_mapping(
    ldap_connection: Connection, discriminator_fields: list[str], dns: set[DN]
) -> dict[DN, dict[str, str | int | None]]:
    dn_list = list(dns)
    mappings = await asyncio.gather(
        *(
            fetch_field_mapping(ldap_connection, discriminator_fields, dn)
            for dn in dn_list
        )
    )
    return dict(zip(dn_list, mappings, strict=True))


@cache
def construct_template(template: str) -> Template:
    from .environments import construct_default_environment

    environment = construct_default_environment()
    return environment.from_string(template)


async def evaluate_template(
    template: str, dn: DN, mapping: dict[str, str | int | None]
) -> bool:
    def mapping2value(field_mapping: dict[str, str | int | None]) -> str | int | None:
        if len(field_mapping) != 1:
            return None
        return one(field_mapping.values())

    jinja_template = construct_template(template)
    result = await jinja_template.render_async(
        dn=dn,
        value=mapping2value(mapping),
        **mapping,
    )
    return result.strip() == "True"


async def filter_dns(
    settings: Settings, ldap_connection: Connection, dns: set[DN]
) -> set[DN]:
    assert isinstance(dns, set)

    discriminator_filter = settings.discriminator_filter
    # If discriminator filter is not configured, no filtering happens
    if not discriminator_filter:
        logger.debug("No discriminator filter set, not filtering")
        return dns

    # We assume discriminator_fields is set if discriminator_filter is
    # This invariant should be upheld by pydantic settings
    discriminator_fields = settings.discriminator_fields
    assert discriminator_fields, "discriminator_fields must be set"

    mapping = await fetch_dn_mapping(ldap_connection, discriminator_fields, dns)
    dns_passing_template = {
        dn
        for dn in dns
        if await evaluate_template(discriminator_filter, dn, mapping[dn])
    }
    logger.info("Discriminator filter run", dns=dns, dns_passing=dns_passing_template)
    return dns_passing_template


async def apply_discriminator(
    settings: Settings, ldap_connection: Connection, dns: set[DN]
) -> DN | None:
    """Find the account to synchronize from a set of DNs.

    The DNs are evaluated depending on the configuration of the discriminator.

    Args:
        dns: The set of DNs to evaluate.

    Raises:
        RequeueMessage: If the provided DNs could not be read from LDAP.
        ValueError: If too many or too few LDAP accounts are found.

    Returns:
        The account to synchronize (if any).
    """
    assert isinstance(dns, set)

    # Empty input-set means we have no accounts to consider
    if not dns:
        return None

    discriminator_fields = settings.discriminator_fields
    # If discriminator is not configured, there can be only one user
    if not discriminator_fields:
        return one(dns)

    # These settings must be set for the function to work
    # This should always be the case, as they are enforced by pydantic
    # But no guarantees are given as pydantic is lenient with run validators
    assert settings.discriminator_values != []

    mapping = await fetch_dn_mapping(ldap_connection, discriminator_fields, dns)

    # If the discriminator_function is template, discriminator values will be a
    # prioritized list of jinja templates (first meaning most important), and we will
    # want to find the best (most important) account.
    # We do this by evaluating the jinja template and looking for outcomes with "True".
    # NOTE: We assume no two accounts are equally important.
    for discriminator in settings.discriminator_values:
        dns_passing_template = {
            dn for dn in dns if await evaluate_template(discriminator, dn, mapping[dn])
        }
        if dns_passing_template:
            return one(
                dns_passing_template,
                too_long=MultipleObjectsReturnedException(
                    f"Ambiguous account result from apply discriminator {dns_passing_template=}"
                ),
            )

    return None


def ldapresponse2entries(ldap_response: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # TODO: Handle other response types
    # See: https://ldap3.readthedocs.io/en/latest/searches.html#response
    return [entry for entry in ldap_response if entry["type"] == "searchResEntry"]


async def _paged_search(
    ldap_connection: Connection,
    searchParameters: dict,
    search_base: str,
    mute: bool,
) -> list[dict[str, Any]]:
    # TODO: Consider using upstream paged_search_generator instead of this?
    # TODO: Eliminate mute argument? - Should be logger configuration?
    # TODO: Find max. paged_size number from LDAP rather than hard-code it?
    searchParameters["paged_size"] = 500
    searchParameters["search_base"] = search_base

    search_filter = searchParameters["search_filter"]

    if not mute:
        logger.info(
            "Executing paged_search",
            search_filter=search_filter,
            search_base=search_base,
        )

    # Max 10_000 pages to avoid eternal loops
    # TODO: Why would we get eternal loops?
    responses: list[dict[str, Any]] = []
    for page in range(0, 10_000):
        if not mute:
            logger.info("Searching page", page=page)
        # TODO: Fetch multiple pages in parallel using asyncio.gather?
        try:
            response, result = await ldap_search(ldap_connection, **searchParameters)
        except LDAPNoSuchObjectResult:
            return responses

        if result["description"] == "operationsError":
            # TODO: Should this be an exception?
            #       Currently we just return half the result?
            logger.warn(
                "Search failed",
                search_filter=search_filter,
                result=result,
            )
            break

        # TODO: Handle this error more gracefully
        assert response is not None
        entries = ldapresponse2entries(response)
        responses.extend(entries)

        try:
            # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
            extension = "1.2.840.113556.1.4.319"
            cookie = result["controls"][extension]["value"]["cookie"]
        except KeyError:
            break

        if cookie and isinstance(cookie, bytes):
            searchParameters["paged_cookie"] = cookie
        else:
            break

    return responses


async def paged_search(
    settings: Settings,
    ldap_connection: Connection,
    searchParameters: dict,
    search_base: str | None = None,
    mute: bool = False,
) -> list:
    """
    Execute a search on the LDAP server.

    Args:
        context: The FastRAMQPI context.
        searchParameters:
            Dict with the following keys:
                * search_filter
                * attributes
        search_base:
            Search base to search in.
            If empty, uses settings.search_base combined with settings.ous_to_search_in.
        mute: Whether to log process information

    Returns:
        A list of search results.
    """
    # NOTE: It seems like this function is purely used for manual endpoints
    #       Except from a single call from usernames.py
    # TODO: Consider moving this to its own module separate from business logic
    # TODO: Make a class for the searchParameters if it has a fixed format?

    if search_base:
        # If the search base is explicitly defined: Don't try anything fancy.
        results = await _paged_search(
            ldap_connection, searchParameters, search_base, mute
        )
        return results

    # Otherwise, loop over all OUs to search in
    search_bases = [
        combine_dn_strings([ou, settings.ldap_search_base])
        for ou in settings.ldap_ous_to_search_in
    ]
    results = []
    for search_base in search_bases:
        results.extend(
            await _paged_search(
                ldap_connection, searchParameters.copy(), search_base, mute
            )
        )

    return results


async def object_search(
    searchParameters: dict[str, Any], ldap_connection: Connection
) -> list[dict[str, Any]]:
    """Performs an LDAP search and return the result.

    Notes:
        If you want to be 100% sure that the search only returns one result;
        Supply an object's dn (distinguished name) as the search base and set
        searchFilter = "(objectclass=*)" and search_scope = BASE

    Args:
        searchParameters:
            Dictionary with the following keys:
                * search_base
                * search_filter
                * attributes
                * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys
        ldap_connection: The LDAP Connection to run our search on.

    Returns:
        A list of found objects.
    """
    search_bases = ensure_list(searchParameters["search_base"])

    responses = []
    # TODO: Asyncio.gather this? - or combine the filters?
    for search_base in search_bases:
        response, _ = await ldap_search(
            ldap_connection, **ChainMap(searchParameters, {"search_base": search_base})
        )
        if response:
            responses.extend(response)
    search_entries = ldapresponse2entries(responses)
    return search_entries


async def single_object_search(
    searchParameters: dict[str, Any],
    ldap_connection: Connection,
) -> dict[str, Any]:
    """Performs an LDAP search and ensure that it returns one result.

    Notes:
        If you want to be 100% sure that the search only returns one result;
        Supply an object's dn (distinguished name) as the search base and set
        searchFilter = "(objectclass=*)" and search_scope = BASE

    Args:
        searchParameters:
            Dictionary with the following keys:
                * search_base
                * search_filter
                * attributes
                * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys
        context: The FastRAMQPI context.

    Raises:
        MultipleObjectsReturnedException: If multiple objects were found.
        NoObjectsReturnedException: If no objects were found.

    Returns:
        The found object.
    """
    no_results_exception = NoObjectsReturnedException(
        f"Found no entries for {searchParameters}"
    )
    try:
        search_entries = await object_search(searchParameters, ldap_connection)
    except LDAPNoSuchObjectResult as e:
        raise no_results_exception from e
    too_long_exception = MultipleObjectsReturnedException(
        f"Found multiple entries for {searchParameters}: {search_entries}"
    )
    return one(
        search_entries,
        too_short=no_results_exception,
        too_long=too_long_exception,
    )


def is_dn(value):
    """
    Determine if a value is a dn (distinguished name) string
    """
    if not isinstance(value, str):
        return False

    try:
        safe_dn(value)
        parse_dn(value)
    except LDAPInvalidDnError:
        return False
    return True


async def get_ldap_object(
    ldap_connection: Connection,
    dn: DN,
    attributes: set | None = None,
    nest: bool = True,
) -> LdapObject:
    """Gets a ldap object based on its DN.

    Args:
        dn: The DN to read.
        context: The FastRAMQPI context.
        nest: Whether to also fetch and nest related objects.
        attributes: The set of attributes to read.

    Returns:
        The LDAP object fetched from the LDAP server.
    """
    if attributes is None:
        attributes = {"*"}

    searchParameters = {
        "search_base": dn,
        "search_filter": "(objectclass=*)",
        "attributes": list(attributes),
        "search_scope": BASE,
    }
    search_result = await single_object_search(searchParameters, ldap_connection)
    dn = search_result["dn"]
    logger.info("Found DN", dn=dn)
    return await make_ldap_object(search_result, ldap_connection, nest=nest)


async def make_ldap_object(
    response: dict, ldap_connection: Connection, nest: bool = True
) -> LdapObject:
    """Takes an LDAP response and formats it as an LdapObject.

    Args:
        response: The LDAP response.
        context: The FastRAMQPI context.
        nest: Whether to also fetch and nest related objects.

    Returns:
        The LDAP object constructed from the response.
    """
    attributes = sorted(list(response["attributes"].keys()))
    ldap_dict = {"dn": response["dn"]}

    async def get_nested_ldap_object(dn):
        """
        Gets a ldap object based on its DN - unless we are in a nested loop
        """

        if nest:
            logger.info("Loading nested ldap object", dn=dn)
            return await get_ldap_object(ldap_connection, dn, nest=False)
        raise Exception("Already running in nested loop")  # pragma: no cover

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
            ldap_dict[attribute] = await get_nested_ldap_object(value)
        elif is_list(value):
            ldap_dict[attribute] = [
                (await get_nested_ldap_object(v)) if is_other_dn(v) and nest else v
                for v in value
            ]
        else:
            ldap_dict[attribute] = value

    return LdapObject(**ldap_dict)


def is_uuid(entity: Any) -> bool:
    """
    Check if a entity is a valid UUID
    """
    with suppress(ValueError):
        UUID(str(entity))
        return True
    return False


def check_ou_in_list_of_ous(ou_to_check, list_of_ous):
    """
    Checks if a specific OU exists in a list of OUs. Raises ValueError if it does not
    """
    any_ok = any(ou_to_check.endswith(ou) for ou in list_of_ous)
    if not any_ok:
        raise ValueError(f"{ou_to_check} is not in {list_of_ous}")


def construct_assertion_control_filter(attributes: dict[str, Any]) -> str:
    """Constructs an LDAP search filter string from a dictionary of attributes.

    This function is useful for constructing LDAP Assertion Controls filter
    in accordance with RFC4515.
    The resulting filter asserts that an LDAP entry must have *all* the specified
    attribute-value pairs.

    NOTE: ldap3.utils.conv.escape_filter_chars for escaping values.

    Args:
        attributes:
            A dictionary where keys are LDAP attribute names and values are the
            expected attribute values.
            Values will be converted to strings and properly escaped.

    Raises:
        ValueError: If 'dn' is a key in the attributes dictionary.

    Returns:
        An LDAP filter string useful for LDAP Assertion Control.
    """
    # Reject asserting anything about DN in the assertion control filter
    # It is nonsensical to do so as the DN is used to target the entity being evaluated
    if "dn" in attributes:
        raise ValueError("Cannot use DN in Assertion Control")

    # We assume that an empty dictionary means "no conditions", i.e. wanting to match
    # any object. '(objectClass=*)' is a common way to represent this.
    if not attributes:
        return "(objectClass=*)"

    def and_filters(filter_pairs: list[str]) -> str:
        # If only a single filter pair is found, simply return it
        if len(filter_pairs) == 1:
            return one(filter_pairs)
        # If multiple filter pairs are found, AND them together
        # The format is (&(filter1)(filter2)...)
        combined_filters = "".join(filter_pairs)
        return f"(&{combined_filters})"

    def generate_pair(key: str, value: Any) -> str:
        value = str(value)
        escaped_value = escape_filter_chars(value)
        # Encoding spaces can be necessary as they may otherwise be stripped by the DC.
        # This is especially true in the case of space-only attribute values,
        # i.e. `description=" "` which may otherwise not be checked correctly.
        encoded_value = escaped_value.replace(" ", r"\20")
        return f"({key}={encoded_value})"

    def generate_pairs(key: str, value: Any) -> str:
        if isinstance(value, list):
            # Empty list values means no value was found on the existing object.
            # In this case we create a filter finding all objects with no value set.
            # This can be done using an inverted (!) match all wildcard (=*)
            if not value:
                return f"(!({key}=*))"
            # Non-empty list values means that a list attribute had some values.
            # In this case we simply add a condition for each value in the list, using
            # the same key for each one ANDing them together at the end, thus saying
            # that the object must have all of these values at once.
            filter_pairs = [generate_pair(key, item) for item in value]
            return and_filters(filter_pairs)
        # Default to just generating a filter pair
        return generate_pair(key, value)

    filter_pairs = [generate_pairs(key, value) for key, value in attributes.items()]
    return and_filters(filter_pairs)


def construct_assertion_control(search_filter: str) -> tuple[str, bool, bytes]:
    """Construct an RFC4528 Assertion Control 3-tuple.

    The goal of the assertion control is to ensure that a write operation only
    takes place if the provided search filter matches an entry on the server.
    It is similar in purpose to ETag (entity tag) within HTTP.

    The control is identified by its Object Identifier (OID) and can be marked
    as critical. If the control is critical and the server does not support it,
    or if the assertion fails, the operation should not be performed.

    Args:
        search_filter:
            String representation of the RFC4515 search filter to check.
            For example: "(objectClass=person)"

    Raises:
        LDAPInvalidFilterError: If the filter is malformed or otherwise invalid.

    Returns:
        A 3-tuple LDAP control, containing:
            Control OID:
                This specifies what kind of control operation must be done.

                This function always returns the OID for assertion control.
                I.e. '1.3.6.1.1.12'.

            Criticality:
                A boolean indicating if the control is critical.
                If set the server must either honorate or refuse the operation.
                Thus if the server does not understand the control it must fail.

                It is possible to check which controls the server supports by reading
                the supportedControl attribute of the server's root DSE.

                This function always returns `True` for criticality.

            Control value:
                The value is an optional argument specific to the Control OID provided.

                In the case of assertion control, it is the BER-encoded assertion
                search filter.
    """
    # Parse the provided filter string into an ldap3 FilterNode
    ldap3_filter: FilterNode = parse_filter(
        search_filter,
        # Skip pre-validating the search filter against a provided schema
        # We will simply let it be validated once it is send to the server
        # All of the following parameters are related to pre-validation
        schema=None,
        auto_escape=True,
        auto_encode=True,
        validator=None,
        check_names=False,
    )
    assert isinstance(ldap3_filter, FilterNode)
    # We assume the generated search-filter only has 1 element (the root)
    root = one(ldap3_filter.elements)
    # Compile the filter into an ASN.1 structure
    asn1_filter: RFC4511Filter = compile_filter(root)
    assert isinstance(asn1_filter, RFC4511Filter)
    # BER encode the ASN.1 filter structure
    ber_encoded_filter = ber_encoder.encode(asn1_filter)

    # Construct and return our 3-tuple, setting criticality to True
    LDAP_ASSERTION_CONTROL_OID = "1.3.6.1.1.12"
    return (LDAP_ASSERTION_CONTROL_OID, True, ber_encoded_filter)
