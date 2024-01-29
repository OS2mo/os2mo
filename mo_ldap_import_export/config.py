# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""
from enum import Enum
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
    import_to_mo: Literal["true", "false", "manual_import_only"] = Field(
        alias="_import_to_mo_"
    )

    @validator("import_to_mo", pre=True)
    def lower_import_to_mo(cls, v: str) -> str:
        return v.lower()

    @root_validator
    def check_uuid_refs_in_mo_objects(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Check that MO objects have a uuid field
        mo_class = import_class(values["objectClass"])

        properties = mo_class.schema()["properties"]
        # If we are dealing with an object that links to a person/org_unit
        # TODO: Add `or "org_unit" in properties`?
        if "person" in properties:
            # Either person or org_unit needs to be set
            has_person = "person" in values
            has_org_unit = "org_unit" in values
            if not has_person and not has_org_unit:
                raise ValueError(
                    "Either 'person' or 'org_unit' key needs to be present"
                )

            # Sometimes only one of them can be set
            required_attributes = get_required_attributes(mo_class)
            requires_person = "person" in required_attributes
            requires_org_unit = "org_unit" in required_attributes
            requires_both = requires_person and requires_org_unit
            if has_person and has_org_unit and not requires_both:
                raise ValueError(
                    "Either 'person' or 'org_unit' key needs to be present. Not both"
                )

            # TODO: What if both are required?
            uuid_key = "person" if "person" in values else "org_unit"
            # And the corresponding item needs to be a dict with an uuid key
            if "dict(uuid=" not in values[uuid_key].replace(" ", ""):
                raise ValueError("Needs to be a dict with 'uuid' as one of its keys")
        # Otherwise: We are dealing with the org_unit/person itself.
        else:
            # A field called 'uuid' needs to be present
            if "uuid" not in values:
                raise ValueError("Needs to contain a key called 'uuid'")
            # And it needs to contain a reference to the employee_uuid global
            if "employee_uuid" not in values["uuid"]:
                raise ValueError("Needs to contain a reference to 'employee_uuid'")
        return values

    @root_validator
    def check_mo_attributes(cls, values: dict[str, Any]) -> dict[str, Any]:
        mo_class = import_class(values["objectClass"])

        accepted_attributes = set(mo_class.schema()["properties"].keys())
        detected_attributes = set(values.keys()) - {"objectClass", "import_to_mo"}

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
    export_to_ldap: Literal["true", "false", "pause"] = Field(alias="_export_to_ldap_")

    @validator("export_to_ldap", pre=True)
    def lower_export_to_ldap(cls, v: str) -> str:
        return v.lower()


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
    username_generator: UsernameGeneratorConfig = Field(
        default_factory=UsernameGeneratorConfig
    )

    @root_validator(skip_on_failure=True)
    def validate_cross_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Check that all mo_to_ldap keys are also in ldap_to_mo
        # Check that all ldap_to_mo keys are also in mo_to_ldap
        mo_to_ldap_user_keys = set(values["mo_to_ldap"].keys())
        ldap_to_mo_user_keys = set(values["ldap_to_mo"].keys())

        # Check that all mo_to_ldap keys are also in ldap_to_mo
        missing_ldap_to_mo = mo_to_ldap_user_keys - ldap_to_mo_user_keys
        if missing_ldap_to_mo:
            raise ValueError(f"Missing keys in 'ldap_to_mo': {missing_ldap_to_mo}")

        # Check that all ldap_to_mo keys are also in mo_to_ldap
        missing_mo_to_ldap = ldap_to_mo_user_keys - mo_to_ldap_user_keys
        if missing_mo_to_ldap:
            raise ValueError(f"Missing keys in 'mo_to_ldap': {missing_mo_to_ldap}")

        return values

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
                    if ldap2mo.address_type != address_type_template:
                        raise ValueError("Address not templating address type UUID")
                case "ramodels.mo.details.it_system.ITUser":
                    it_system_template = (
                        f"{{{{ dict(uuid=get_it_system_uuid('{key}')) }}}}"
                    )
                    if ldap2mo.itsystem != it_system_template:
                        raise ValueError("IT-System not templating it-system UUID")
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


class AuthBackendEnum(str, Enum):
    NTLM = "ntlm"
    SIMPLE = "simple"


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    conversion_mapping: ConversionMapping = Field(
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
    ldap_auth_method: AuthBackendEnum = Field(
        AuthBackendEnum.NTLM, description="The auth backend to use."
    )
    ldap_unique_id_field: str = Field(
        "objectGUID",
        description="Name of the attribute that holds the server-assigned unique identifier. `objectGUID` on Active Directory and `entryUUID` on most standard LDAP implementations (per RFC4530).",
    )

    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )

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
