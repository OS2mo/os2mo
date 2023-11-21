# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""
from typing import Any
from typing import Literal

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import ConstrainedList
from pydantic import Extra
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import PositiveInt
from pydantic import root_validator
from pydantic import SecretStr
from pydantic import validator
from ramqp.config import AMQPConnectionSettings

from .utils import import_class


class ServerConfig(BaseModel):
    """Settings model for domain controllers."""

    class Config:
        """Settings are frozen."""

        frozen = True

    host: str = Field(..., description="Hostname / IP to establish connection with")
    port: int | None = Field(
        None,
        description=(
            "Port to utilize when establishing a connection. Defaults to 636 for SSL"
            " and 389 for non-SSL"
        ),
    )
    use_ssl: bool = Field(False, description="Whether to establish a SSL connection")
    insecure: bool = Field(False, description="Whether to verify SSL certificates")
    timeout: int = Field(5, description="Number of seconds to wait for connection")


class ServerList(ConstrainedList):
    """Constrainted list for domain controllers."""

    min_items = 1
    unique_items = True

    item_type = ServerConfig
    __args__ = (ServerConfig,)


class InternalAMQPConnectionSettings(AMQPConnectionSettings):
    exchange = "ldap_ie_internal"
    queue_prefix = "ldap_ie_internal"
    prefetch_count = 1  # MO cannot handle too many requests


class ExternalAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "ldap_ie"
    prefetch_count: int = 1  # MO cannot handle too many requests


class FastFAMQPIApplicationSettings(FastRAMQPISettings):
    mo_graphql_version: PositiveInt = 7
    amqp: ExternalAMQPConnectionSettings


class MappingBaseModel(BaseModel):
    class Config:
        frozen = True
        extra = Extra.forbid


class Class(MappingBaseModel):
    title: str
    scope: str


class Init(MappingBaseModel):
    # facet_user_key: {class_user_key: class}
    facets: dict[str, dict[str, Class]] = {}
    # user_key: name
    it_systems: dict[str, str] = {}


def get_required_attributes(mo_class) -> set[str]:
    if "required" not in mo_class.schema().keys():
        return set()
    return set(mo_class.schema()["required"])


def check_attributes(
    detected_attributes: set[str], accepted_attributes: set[str]
) -> None:
    unacceptable_attributes = detected_attributes - accepted_attributes
    # SAM Account Name is specifically allowed
    # TODO: Why?
    unacceptable_attributes.discard("sAMAccountName")
    # All extensionAttributes and special attributes are allowed
    # TODO: Why?
    unacceptable_attributes = {
        attribute
        for attribute in unacceptable_attributes
        if not attribute.startswith("extensionAttribute")
        and not attribute.startswith("__")
    }
    if unacceptable_attributes:
        raise ValueError(
            f"Attributes {unacceptable_attributes} are not allowed. "
            f"The following attributes are allowed: {accepted_attributes}"
        )


class LDAP2MOMapping(MappingBaseModel):
    class Config:
        extra = Extra.allow

    objectClass: str
    _import_to_mo_: bool

    @root_validator
    def check_mo_attributes(cls, values: dict[str, Any]) -> dict[str, Any]:
        mo_class = import_class(values["objectClass"])

        accepted_attributes = set(mo_class.schema()["properties"].keys())
        detected_attributes = set(values.keys()) - {"objectClass", "_import_to_mo_"}

        check_attributes(detected_attributes, accepted_attributes)

        required_attributes = get_required_attributes(mo_class)
        if values["objectClass"] == "ramodels.mo.details.engagement.Engagement":
            # We require a primary attribute. If primary is not desired you can set
            # it to {{ NONE }} in the json dict
            required_attributes.add("primary")

        missing_attributes = required_attributes - detected_attributes
        if missing_attributes:
            raise ValueError(
                f"Missing {missing_attributes} which are mandatory. "
                f"The following attributes are mandatory: {required_attributes}"
            )
        return values


class MO2LDAPMapping(MappingBaseModel):
    class Config:
        extra = Extra.allow

    objectClass: str
    _import_to_ldap_: bool


class UsernameGeneratorConfig(MappingBaseModel):
    objectClass: str = "UserNameGenerator"
    char_replacement: dict[str, str] = {}
    forbidden_usernames: list[str] = []
    combinations_to_try: list[str] = []

    @validator("combinations_to_try")
    def check_combinations(cls, v: list[str]) -> list[str]:
        # Validator for combinations_to_try
        accepted_characters = ["F", "L", "1", "2", "3", "X"]
        for combination in v:
            if not all([c in accepted_characters for c in combination]):
                raise ValueError(
                    f"Incorrect combination found: '{combination}' username "
                    f"combinations can only contain {accepted_characters}"
                )
        return v


class ConversionMapping(MappingBaseModel):
    init: Init = Field(default_factory=Init)
    ldap_to_mo: dict[str, LDAP2MOMapping]
    mo_to_ldap: dict[str, MO2LDAPMapping]
    username_generator: UsernameGeneratorConfig

    @root_validator(skip_on_failure=True)
    def validate_address_types(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that address_type attributes are formatted properly."""
        for key, ldap2mo in values["ldap_to_mo"].items():
            object_class = ldap2mo.objectClass
            match object_class:
                case "ramodels.mo.details.address.Address":
                    if hasattr(ldap2mo, "org_unit"):
                        address_type_template = f"{{{{ dict(uuid=get_org_unit_address_type_uuid('{key}')) }}}}"
                    else:
                        address_type_template = f"{{{{ dict(uuid=get_employee_address_type_uuid('{key}')) }}}}"
                    assert ldap2mo.address_type == address_type_template
                case "ramodels.mo.details.it_system.ITUser":
                    it_system_template = (
                        f"{{{{ dict(uuid=get_it_system_uuid('{key}')) }}}}"
                    )
                    assert ldap2mo.itsystem == it_system_template
        return values

    @root_validator(skip_on_failure=True)
    def validate_init_entries_used(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that all entries created on init are used in mappings."""
        it_system_user_keys = set(values["init"].it_systems.keys())
        class_user_keys = {
            class_user_key
            for classes in values["init"].facets.values()
            for class_user_key in classes.keys()
        }

        init_user_keys = class_user_keys | it_system_user_keys
        mapped_user_keys = set(values["mo_to_ldap"].keys())

        unutilized_user_keys = init_user_keys - mapped_user_keys
        if unutilized_user_keys:
            raise ValueError("Unutilized elements in init configuration")

        return values


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    conversion_mapping: ConversionMapping | None = Field(
        default=None,
        description="Conversion mapping between LDAP and OS2mo",
    )

    internal_amqp: InternalAMQPConnectionSettings = Field(
        default_factory=InternalAMQPConnectionSettings,  # type: ignore
        description="Internal amqp settings",
    )

    fastramqpi: FastFAMQPIApplicationSettings

    listen_to_changes_in_mo: bool = Field(
        True, description="Whether to write to AD, when changes in MO are registered"
    )

    listen_to_changes_in_ldap: bool = Field(
        True, description="Whether to write to MO, when changes in LDAP are registered"
    )

    add_objects_to_ldap: bool = Field(
        True,
        description=(
            "If True: Adds new objects to LDAP "
            "when an object is in MO but not in LDAP. "
            "If False: Only modifies existing objects."
        ),
    )

    ldap_controllers: ServerList = Field(
        ..., description="List of domain controllers to query"
    )
    ldap_domain: str = Field(
        ..., description="Domain to use when authenticating with the domain controller"
    )
    ldap_user: str = Field(
        "os2mo",
        description="Username to use when authenticating with the domain controller",
    )
    ldap_password: SecretStr = Field(
        ...,
        description="Password to use when authenticating with the domain controller",
    )
    ldap_search_base: str = Field(
        ..., description="Search base to utilize for all LDAP requests"
    )
    ldap_ous_to_search_in: list[str] = Field(
        [""],
        description=(
            "List of OUs to search in. If this contains an empty string; "
            "Searches in all OUs in the search base"
        ),
    )
    ldap_ous_to_write_to: list[str] = Field(
        [""],
        description=(
            "List of OUs to write to. If this contains an empty string; "
            "Writes to all OUs in the search base"
        ),
    )
    ldap_ou_for_new_users: str = Field(
        "", description="OU to create new users in. For example 'OU=Test'"
    )

    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )

    client_id: str = Field("bruce", description="Client ID for OIDC client.")
    client_secret: SecretStr = Field(..., description="Client Secret for OIDC client.")
    auth_server: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://keycloak-service:8080/auth"),
        description="Base URL for OIDC server (Keycloak).",
    )
    auth_realm: str = Field("mo", description="Realm to authenticate against")

    graphql_timeout: int = 120

    default_org_unit_type: str = Field(
        ..., description="Type to set onto imported organization units"
    )

    default_org_unit_level: str = Field(
        ..., description="Level to set onto imported organization units"
    )

    org_unit_path_string_separator: str = Field(
        "\\", description="separator for full paths to org units in LDAP"
    )

    poll_time: float = Field(
        5, description="Seconds between calls to LDAP to search for updates"
    )

    check_alleroed_sd_number: bool = Field(
        False,
        description=(
            "Check that an SD-employee number does not start with 9, "
            "before writing to LDAP"
        ),
    )

    it_user_to_check: str = Field(
        "",
        description=(
            "Check that an employee has an it-user with this user_key "
            "before writing to LDAP"
        ),
    )

    check_holstebro_ou_issue_57426: list[str] = Field(
        [],
        description="Check that OU is below or equal one of these, see #57426",
    )

    discriminator_function: Literal["exclude", "include", None] = Field(
        None,
        description="The type of discriminator function, either include or exclude",
    )

    discriminator_field: str | None = Field(
        None, description="The field to look for discriminator values in"
    )

    discriminator_values: list[str] = Field(
        [], description="The values used for discrimination"
    )
