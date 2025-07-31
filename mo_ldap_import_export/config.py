# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""

from contextlib import suppress
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Literal
from uuid import UUID

import structlog
import yaml
from fastramqpi.config import Settings as FastRAMQPISettings
from fastramqpi.ramqp.config import AMQPConnectionSettings
from fastramqpi.ramqp.mo import MORoutingKey
from jinja2 import Environment
from jinja2 import TemplateSyntaxError
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import ConstrainedList
from pydantic import Extra
from pydantic import Field
from pydantic import SecretStr
from pydantic import parse_obj_as
from pydantic import root_validator
from pydantic import validator

from .models import Employee
from .models import MOBase
from .types import LDAPUUID
from .utils import import_class

logger = structlog.stdlib.get_logger()


SLEEP_ON_ERROR = 30


class JinjaTemplate(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")
        # Validate that the jinja template can be parsed correctly
        try:
            env = Environment()
            env.parse(v)
        except TemplateSyntaxError as e:
            message = "Unable to parse jinja"
            logger.exception(message)
            raise ValueError(message) from e
        return v

    def __repr__(self):
        return f"JinjaTemplate({super().__repr__()})"


def value_or_default(dicty: dict[str, Any], key: str, default: Any) -> None:
    dicty[key] = dicty.get(key) or default


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
    ca_certs_data: str | None = Field(
        None, description="The CA chain to verify SSL with"
    )
    insecure: bool = Field(False, description="Whether to verify SSL certificates")
    timeout: int = Field(5, description="Number of seconds to wait for connection")


class ServerList(ConstrainedList):
    """Constrainted list for domain controllers."""

    min_items = 1
    unique_items = True

    item_type = ServerConfig
    __args__ = (ServerConfig,)


class LDAPAMQPConnectionSettings(AMQPConnectionSettings):
    exchange = "ldap_ie_ldap"
    queue_prefix = "ldap_ie_ldap"
    prefetch_count = 1  # MO cannot handle too many requests


class ExternalAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "ldap_ie"
    upstream_exchange = "os2mo"
    prefetch_count: int = 1  # MO cannot handle too many requests

    @root_validator
    def set_exchange_by_queue_prefix(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that exchange is set based on queue_prefix."""
        values["exchange"] = "os2mo_" + values["queue_prefix"]
        return values


class FastFAMQPIApplicationSettings(FastRAMQPISettings):
    amqp: ExternalAMQPConnectionSettings


class MappingBaseModel(BaseModel):
    class Config:
        frozen = True
        extra = Extra.forbid


def get_required_attributes(mo_class) -> set[str]:
    if "required" not in mo_class.schema():
        return set()
    return set(mo_class.schema()["required"])


class LDAP2MOMapping(MappingBaseModel):
    class Config:
        extra = Extra.allow

    objectClass: str
    import_to_mo: Literal["true", "edit_only", "false"] = Field(alias="_import_to_mo_")
    terminate: str | None = Field(
        alias="_terminate_", description="The date at which to terminate the object"
    )
    ldap_attributes: list[str] = Field(
        ...,
        alias="_ldap_attributes_",
        description="The attributes to fetch for LDAP, aka attributes available on the ldap object in templates",
    )

    def as_mo_class(self) -> type[MOBase]:
        return import_class(self.objectClass)

    def get_fields(self) -> dict[str, Any]:
        return self.dict(
            exclude={"objectClass", "import_to_mo", "terminate", "ldap_attributes"},
            by_alias=True,
            exclude_unset=True,
        )

    @validator("import_to_mo", pre=True)
    def lower_import_to_mo(cls, v: str) -> str:
        return v.lower()

    @root_validator
    def check_edit_only_set_for_employee(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that edit_only is only set on employees."""
        if (
            "import_to_mo" not in values
            or not values["import_to_mo"]
            or values["import_to_mo"] != "edit_only"
        ):
            return values

        mo_class = import_class(values["objectClass"])
        if mo_class is not Employee:
            raise ValueError("Edit only is only supported for employees")
        return values

    @root_validator
    def check_uuid_set_if_terminate_set(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that uuid is set if terminate is set."""
        if not values["terminate"]:
            return values

        if "uuid" not in values:
            raise ValueError("UUID must be set if _terminate_ is set")

        if not values["uuid"]:
            raise ValueError("UUID must not be empty if _terminate_ is set")

        return values

    @root_validator
    def check_terminate_not_set_on_employee(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure that terminate is not set on employee, which you cannot terminate."""
        if not values["terminate"]:
            return values

        mo_class = import_class(values["objectClass"])
        if mo_class is Employee:
            raise ValueError("Termination not supported for employee")

        return values

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
        else:  # Otherwise: We are dealing with the org_unit/person itself.
            # A field called 'uuid' needs to be present
            if "uuid" not in values:
                raise ValueError("Needs to contain a key called 'uuid'")
        return values

    @root_validator
    def check_mo_attributes(cls, values: dict[str, Any]) -> dict[str, Any]:
        mo_class = import_class(values["objectClass"])

        accepted_attributes = set(mo_class.schema()["properties"].keys())
        detected_attributes = set(values.keys()) - {
            "objectClass",
            "import_to_mo",
            "terminate",
            "ldap_attributes",
        }
        # Disallow validity until we introduce a consistent behavior in the future
        if "validity" in detected_attributes:
            raise ValueError("'validity' cannot be set on the ldap_to_mo mapping")

        superfluous_attributes = detected_attributes - accepted_attributes
        if superfluous_attributes:
            raise ValueError(
                f"Attributes {superfluous_attributes} are not allowed. "
                f"The following attributes are allowed: {accepted_attributes}"
            )

        required_attributes = get_required_attributes(mo_class)
        if values["objectClass"] == "Engagement":
            # We require a primary attribute. If primary is not desired you can set
            # it to {{ NONE }} in the json dict
            required_attributes.add("primary")

        # Validity is no longer required, as we default to last midnight
        required_attributes.discard("validity")

        missing_attributes = required_attributes - detected_attributes
        if missing_attributes:
            raise ValueError(
                f"Missing {missing_attributes} which are mandatory. "
                f"The following attributes are mandatory: {required_attributes}"
            )
        return values


class UsernameGeneratorConfig(MappingBaseModel):
    # TODO: This default is not desired, but kept here for backwards compatability.
    #       In the future it should be moved to the salt-automation configuration.
    #       And the default here should be removed entirely.
    # TODO: Perhaps it would be desirable to remove the other UsernameGenerator
    #       entirely instead opting to simply have one which is configurable.
    #       I.e. check MO for usernames if `existing_usernames_itsystem` is set.
    existing_usernames_itsystem: str = "ADSAMA"
    char_replacement: dict[str, str] = {}
    forbidden_usernames: list[str] = []
    combinations_to_try: list[str] = []
    remove_vowels: bool = False
    disallow_mo_usernames: bool = False
    reuse_old_usernames: bool = Field(
        False, description="Allow reusing a user's previously allocated usernames"
    )

    @validator("forbidden_usernames")
    def casefold_forbidden_usernames(cls, v: list[str]) -> list[str]:
        return [u.casefold() for u in v]

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


class MO2LDAPMapping(MappingBaseModel):
    identifier: str
    routing_key: MORoutingKey
    template: JinjaTemplate
    object_class: str


class ConversionMapping(MappingBaseModel):
    ldap_to_mo: dict[str, LDAP2MOMapping] | None = None
    ldap_to_mo_any: dict[str, dict[str, LDAP2MOMapping]] = Field(
        default_factory=dict,
        description="""
        LDAP to MO mapping.

        Outer-dict keys are the objectClass for which the mapping will be called.
        The inner-mapping is equivalent to `ldap_to_mo_org_unit`.
        """,
    )
    mo2ldap: JinjaTemplate | None = Field(
        None, description="MO to LDAP mapping template"
    )
    mo_to_ldap: list[MO2LDAPMapping] = Field(
        default_factory=list, description="MO to LDAP mappings"
    )
    username_generator: UsernameGeneratorConfig = Field(
        default_factory=UsernameGeneratorConfig
    )


class AuthBackendEnum(str, Enum):
    NTLM = "ntlm"
    SIMPLE = "simple"


def yaml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    # https://docs.pydantic.dev/1.10/usage/settings/#adding-sources
    encoding = settings.__config__.env_file_encoding
    try:
        text = Path("/var/run/config.yaml").read_text(encoding)
    except FileNotFoundError:
        return {}
    config: dict[str, Any] = yaml.load(text, yaml.SafeLoader)
    return {k.lower(): v for k, v in config.items()}


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
                file_secret_settings,
            )

    conversion_mapping: ConversionMapping = Field(
        description="Conversion mapping between LDAP and OS2mo",
    )

    ldap_amqp: LDAPAMQPConnectionSettings = Field(
        default_factory=LDAPAMQPConnectionSettings,  # type: ignore
        description="LDAP amqp settings",
    )

    fastramqpi: FastFAMQPIApplicationSettings

    @root_validator(pre=True)
    def share_amqp_url(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Use FastRAMQPI__AMQP__URL as a default for AMQP URLs"""
        # If a key-error occurs, do nothing and let the validation explain it
        with suppress(KeyError):
            fastramqpi_amqp_url = values["fastramqpi"]["amqp"]["url"]

            values["ldap_amqp"] = values.get("ldap_amqp", {})
            values["ldap_amqp"]["url"] = values["ldap_amqp"].get(
                "url", fastramqpi_amqp_url
            )
        return values

    listen_to_changes_in_mo: bool = Field(
        True, description="Whether to write to AD, when changes in MO are registered"
    )

    listen_to_changes_in_ldap: bool = Field(
        True, description="Whether to write to MO, when changes in LDAP are registered"
    )

    mo_uuids_to_ignore: list[UUID] = Field(
        default_factory=list,
        description="Set of MO UUIDs to ignore changes to",
    )

    ldap_uuids_to_ignore: list[LDAPUUID] = Field(
        default_factory=list,
        description="Set of LDAP UUIDs to ignore changes to",
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

    @validator("ldap_controllers")
    def check_at_most_one_controller(cls, v: list[ServerConfig]) -> list[ServerConfig]:
        # Validate that at most one domain controller is configured
        # Domain controllers have no strong guarantee of when replication is done,
        # thus if we generate an event from one domain controller, the data may not
        # yet be available on another domain controller, so events and processing of
        # them must be done on the same domain controllers, or a check must be in place
        # to ensure that the current domain controller is up-to-date with the replica
        # we got the event from. This all gets really complex really fast, so instead
        # we just limit ourselves to a single domain controller for now.
        if len(v) > 1:
            raise ValueError("At most one domain controller can be configured")
        return v

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

    ldap_object_class: str = Field(
        ..., description="The LDAP object class that contains the CPR number"
    )
    ldap_cpr_attribute: str | None = Field(
        None,
        description="The attribute (if any) that contains the CPR number in LDAP",
    )
    ldap_it_system: str | None = Field(
        None,
        description="The user-key (if any) of the ADGUID IT-system in MO",
    )

    @root_validator
    def check_ldap_correlation_key(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values["ldap_cpr_attribute"] is None and values["ldap_it_system"] is None:
            raise ValueError(
                "'LDAP_CPR_ATTRIBUTE' and 'LDAP_IT_SYSTEM' cannot both be 'None'. "
                "Atleast one must be set to allow for MO<-->LDAP correlation."
            )
        return values

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
    ldap_dialect: Literal["Standard", "AD"] = Field(
        "AD", description="Which LDAP dialect to use"
    )
    ldap_unique_id_field: str = Field(
        "",
        description="Name of the attribute that holds the server-assigned unique identifier. `objectGUID` on Active Directory and `entryUUID` on most standard LDAP implementations (per RFC4530).",
    )
    ldap_user_objectclass: str = Field("", description="Object class for users")

    @root_validator
    def set_dialect_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Root-validator to set LDAP dialect specific defaults.

        This validator exists to ease the configuration of the component if one uses a
        one of the supported LDAP dialects.
        """
        dialect = values.get("ldap_dialect", "UNKNOWN")
        if dialect == "Standard":
            value_or_default(values, "ldap_unique_id_field", "entryUUID")
            value_or_default(values, "ldap_user_objectclass", "inetOrgPerson")
        if dialect == "AD":
            value_or_default(values, "ldap_unique_id_field", "objectGUID")
            value_or_default(values, "ldap_user_objectclass", "user")
        return values

    # NOTE: It appears that this flag does not in fact work
    # See: https://github.com/cannatag/ldap3/issues/1008
    ldap_read_only: bool = Field(
        False, description="Whether to establish a read-only connection to the server."
    )
    ldap_receive_timeout: int = Field(
        10, description="Number of seconds to wait for communication (wire timeout)."
    )
    ldap_response_timeout: int = Field(
        10, description="Number of seconds to wait for responses (query timeout)."
    )

    # TODO: Remove this, as it already exists within FastRAMQPI?
    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )

    org_unit_path_string_separator: str = Field(
        "\\", description="separator for full paths to org units in LDAP"
    )

    poll_time: float = Field(
        5, description="Seconds between calls to LDAP to search for updates"
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

    discriminator_fields: list[str] = Field(
        [], description="The fields to provide to the discriminator template"
    )

    @root_validator
    def check_for_invalid_discriminator_fields(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure that discriminator fields do not contain invalid values."""
        discriminator_fields = values["discriminator_fields"]
        for key in ["dn", "value"]:
            if key in discriminator_fields:
                raise ValueError(f"Invalid field in DISCRIMINATOR_FIELD(S): '{key}'")

        return values

    discriminator_values: list[JinjaTemplate] = Field(
        [], description="The values used for discrimination"
    )

    discriminator_filter: JinjaTemplate | None = Field(
        None,
        description="Jinja filter to run before applying the discriminator",
    )

    @root_validator
    def check_discriminator_filter_settings(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure that discriminator fields is set, if filter is set."""
        # No discriminator_filter, not required fields
        if (
            "discriminator_filter" not in values
            or values["discriminator_filter"] is None
        ):
            return values
        # No discriminator_field, not we have a problem
        if values["discriminator_fields"] == []:
            raise ValueError(
                "DISCRIMINATOR_FIELD(s) must be set, if DISCRIMINATOR_FILTER is set"
            )
        return values

    @root_validator
    def check_discriminator_settings(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure that discriminator function and values is set, if field is set."""
        # No discriminator_field, not required fields
        if values["discriminator_fields"] == []:
            return values
        assert "discriminator_values" in values
        # Check that our now required fields are set
        if values["discriminator_values"] == []:
            raise ValueError(
                "DISCRIMINATOR_VALUES must be set, if DISCRIMINATOR_FIELD is set"
            )
        return values

    create_user_trees: list[UUID] = Field(
        default_factory=list,
        description=(
            "Only create users with primary engagement in the specified MO organization"
            "units or their subtrees, the empty list allows creating all MO users"
        ),
    )
