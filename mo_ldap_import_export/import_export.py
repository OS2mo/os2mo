# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import json
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterator
from collections.abc import Sequence
from contextlib import ExitStack
from functools import wraps
from typing import Any
from typing import TypeVar
from typing import cast
from uuid import UUID
from uuid import uuid4

import structlog
from fastramqpi.ramqp.depends import handle_exclusively_decorator
from ldap3 import Connection
from more_itertools import one
from more_itertools import partition
from structlog.contextvars import bound_contextvars

from .config import LDAP2MOMapping
from .config import Settings
from .converters import LdapConverter
from .customer_specific_checks import ExportChecks
from .customer_specific_checks import ImportChecks
from .dataloaders import DN
from .dataloaders import DataLoader
from .exceptions import IncorrectMapping
from .exceptions import SkipObject
from .ldap import apply_discriminator
from .ldap import filter_dns
from .ldap import get_ldap_object
from .moapi import Verb
from .moapi import get_primary_engagement
from .models import Address
from .models import Employee
from .models import Engagement
from .models import ITUser
from .models import JobTitleFromADToMO
from .models import MOBase
from .models import Termination
from .types import EmployeeUUID
from .types import OrgUnitUUID
from .utils import ensure_list
from .utils import mo_today
from .utils import star

logger = structlog.stdlib.get_logger()


T = TypeVar("T", covariant=True)


def with_exitstack(
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Inject an exit-stack into decorated function.

    Args:
        func: The function to inject the exit-stack into.

    Returns:
        Decorated function that takes the exit-stack as an argument.
    """

    @wraps(func)
    async def inner(*args: Any, **kwargs: Any) -> Any:
        with ExitStack() as exit_stack:
            return await func(*args, **kwargs, exit_stack=exit_stack)

    return inner


class SyncTool:
    def __init__(
        self,
        dataloader: DataLoader,
        converter: LdapConverter,
        export_checks: ExportChecks,
        import_checks: ImportChecks,
        settings: Settings,
        ldap_connection: Connection,
    ) -> None:
        self.dataloader: DataLoader = dataloader
        self.converter: LdapConverter = converter
        self.export_checks: ExportChecks = export_checks
        self.import_checks: ImportChecks = import_checks
        self.settings: Settings = settings
        self.ldap_connection: Connection = ldap_connection

    @staticmethod
    def wait_for_import_to_finish(func: Callable):
        """Runs the function while ensuring sequentiality w.r.t. the dn parameter."""

        def dn_extractor(self, *args, **kwargs):
            dn = args[0] if args else kwargs["dn"]
            logger.info("Generating DN", dn=dn)
            return dn

        return handle_exclusively_decorator(dn_extractor)(func)

    async def perform_export_checks(self, employee_uuid: UUID) -> None:
        """
        Perform a number of customer-specific checks. Raising IgnoreChanges() if a
        check fails
        """

        # Check that the employee has an it-user with user_key = it_user_to_check
        await self.export_checks.check_it_user(
            employee_uuid,
            self.settings.it_user_to_check,
        )

    async def perform_import_checks(self, dn: str, json_key: str) -> bool:
        if self.settings.check_holstebro_ou_issue_57426:  # pragma: no cover
            return await self.import_checks.check_holstebro_ou_is_externals_issue_57426(
                self.settings.check_holstebro_ou_issue_57426,
                dn,
                json_key,
            )
        return True

    async def render_ldap2mo(self, uuid: EmployeeUUID, dn: DN) -> dict[str, list[Any]]:
        await self.perform_export_checks(uuid)

        mo2ldap_template = self.settings.conversion_mapping.mo2ldap
        assert mo2ldap_template is not None
        template = self.converter.environment.from_string(mo2ldap_template)
        result = await template.render_async({"uuid": uuid, "dn": dn})
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert all(isinstance(key, str) for key in parsed)
        # Convert None's to empty lists to avoid writing "None" in LDAP
        # Whenever a None is templated out we empty the value in LDAP
        parsed = {key: [] if value is None else value for key, value in parsed.items()}
        # TODO: force users to configure as list instead of implicitly
        # converting (very confusing).
        # assert all(isinstance(value, list) for value in parsed.values())
        return {key: ensure_list(value) for key, value in parsed.items()}

    async def create_ituser_link(self, uuid: EmployeeUUID, dn: DN) -> None:
        # Check if we even dare create a DN
        raw_it_system_uuid = await self.dataloader.moapi.get_ldap_it_system_uuid()
        if raw_it_system_uuid is None:
            return None

        # If the LDAP ITSystem exists, we want to create a binding to our newly
        # generated (and created) DN, such that it can be correlated in the future.
        #
        # NOTE: This may not be executed if the program crashes after creating the LDAP
        #       account, but before creating this ituser link.
        #       Thus the current code is not robust and may fail at any time.
        #       The appropriate solution here is either to ensure that the LDAP account
        #       and the ituser link are created atomically or to introduce a multi-stage
        #       commit solution to the integration.
        #       One practical solution may be to entirely eliminate the need for these
        #       ituser links by allocating a field in LDAP for the MO UUID and using
        #       that field to link MO and LDAP accounts together.
        #       An alternative solution may involve writing a temporary dummy value to
        #       LDAP on the initial create which can be detected later to ensure that
        #       creation is completed even if the program crashes at an inopportune
        #       time. - The risk of this approach is that we have bad values in LDAP,
        #       which may be synchronized by other listeners on LDAP, and thus have
        #       unforseen consequences.
        logger.info("No ITUser found, creating one to correlate with DN", dn=dn)
        # Get its unique ldap uuid
        # TODO: Get rid of this code and operate on EntityUUIDs thoughout
        unique_uuid = await self.dataloader.ldapapi.get_ldap_unique_ldap_uuid(dn)
        logger.info("LDAP UUID found for DN", dn=dn, ldap_uuid=unique_uuid)
        # Make a new it-user
        it_user = ITUser(
            user_key=str(unique_uuid),
            itsystem=UUID(raw_it_system_uuid),
            person=uuid,
            validity={"start": mo_today()},
        )
        await self.dataloader.moapi.create_ituser(it_user)

    async def may_create_user_given_orgunit_location(self, uuid: EmployeeUUID) -> bool:
        create_user_trees = set(self.settings.create_user_trees)
        # Empty set, means nothing to check, which means we will create
        if not create_user_trees:
            logger.debug("create_user_trees not configured, allowing create")
            return True

        primary_engagement_uuid = await get_primary_engagement(
            self.dataloader.moapi.graphql_client, uuid
        )
        if primary_engagement_uuid is None:
            logger.info(
                "create_user_trees configured, but no primary engagement, skipping"
            )
            return False

        fetched_engagement = await self.dataloader.moapi.load_mo_engagement(
            primary_engagement_uuid, end=None
        )
        if fetched_engagement is None:
            logger.info("create_user_trees engagement is not current or future")
            return False

        org_unit_uuid = fetched_engagement.org_unit
        if org_unit_uuid in create_user_trees:
            return True

        # Converting ancestors to a set, as we do not care which ancestor is found
        ancestors = set(
            await self.dataloader.moapi.get_ancestors(OrgUnitUUID(org_unit_uuid))
        )
        # If any ancestor is overlapping with the create_user_trees UUIDs we match
        overlap = create_user_trees.intersection(ancestors)
        return bool(overlap)

    @with_exitstack
    async def listen_to_changes_in_employees(
        self,
        uuid: EmployeeUUID,
        exit_stack: ExitStack,
        dry_run: bool = False,
    ) -> dict[str, list[Any]]:
        """Synchronize employee data from MO to LDAP.

        Args:
            uuid: UUID of the changed employee.
            exit_stack: The injected exit-stack.
        """
        exit_stack.enter_context(bound_contextvars(uuid=str(uuid)))
        logger.info("Registered change in an employee")

        mo2ldap_template = self.settings.conversion_mapping.mo2ldap
        if not mo2ldap_template:
            logger.info("listen_to_changes_in_employees called without mapping")
            return {}

        best_dn, create = await self.dataloader._find_best_dn(uuid, dry_run=dry_run)
        if best_dn is None:
            return {}

        if create:
            is_ok = await self.may_create_user_given_orgunit_location(uuid)
            if not is_ok:
                logger.info("Primary engagement OU outside create_user_trees, skipping")
                return {}

        exit_stack.enter_context(bound_contextvars(dn=best_dn))
        ldap_desired_state = await self.render_ldap2mo(uuid, best_dn)

        # If dry-running we do not want to makes changes in LDAP
        if dry_run:
            logger.info("Not writing to LDAP due to dry-running", dn=best_dn)
            return ldap_desired_state

        if not ldap_desired_state:
            logger.info("Not writing to LDAP as changeset is empty", dn=best_dn)
            return {}

        if create:
            await self.dataloader.ldapapi.add_ldap_object(best_dn, ldap_desired_state)
            await self.create_ituser_link(uuid, best_dn)
        else:
            # To avoid spamming server logs we compare with current state before writing
            # Without this the LDAP / AD server will register lots of empty writes
            current_state = await get_ldap_object(
                self.ldap_connection,
                best_dn,
                attributes=set(ldap_desired_state.keys()),
                # Nest false is required, as otherwise we compare an object with a DN string
                nest=False,
            )
            current_state_dict = current_state.dict()
            current_state_dict = {
                key.lower(): value for key, value in current_state_dict.items()
            }
            ldap_changes = {
                key: value
                for key, value in ldap_desired_state.items()
                # We use ensure_list as it is done already to render_ldap2mo
                if (
                    key.lower() not in current_state_dict
                    or ensure_list(current_state_dict[key.lower()]) != value
                )
            }
            await self.dataloader.ldapapi.modify_ldap_object(best_dn, ldap_changes)

        return ldap_desired_state

    async def fetch_uuid_object(
        self, uuid: UUID, mo_class: type[MOBase]
    ) -> MOBase | None:
        # This type is not handled by this function
        assert not issubclass(mo_class, Termination)

        if issubclass(mo_class, Address):
            return await self.dataloader.moapi.load_mo_address(
                uuid, current_objects_only=False
            )
        if issubclass(mo_class, Engagement):
            return await self.dataloader.moapi.load_mo_engagement(
                uuid, start=None, end=None
            )
        if issubclass(mo_class, ITUser):
            return await self.dataloader.moapi.load_mo_it_user(
                uuid, current_objects_only=False
            )
        if issubclass(mo_class, Employee):
            return await self.dataloader.moapi.load_mo_employee(
                uuid, current_objects_only=False
            )
        raise AssertionError(f"Unknown mo_class: {mo_class}")

    async def construct_uuid_mapping(
        self,
        converted_objects: Sequence[MOBase],
    ) -> list[tuple[MOBase, MOBase | None]]:
        mo_class = one({type(o) for o in converted_objects})

        return [
            (
                converted_object,
                await self.fetch_uuid_object(converted_object.uuid, mo_class),
            )
            for converted_object in converted_objects
        ]

    def get_mapping(self, json_key: str) -> LDAP2MOMapping:
        assert self.settings.conversion_mapping.ldap_to_mo is not None
        try:
            return self.settings.conversion_mapping.ldap_to_mo[json_key]
        except KeyError as error:  # pragma: no cover
            raise IncorrectMapping(
                f"Missing '{json_key}' in mapping 'ldap_to_mo'"
            ) from error

    async def format_converted_objects(
        self,
        converted_objects: Sequence[MOBase | Termination],
        mo_attributes: set[str],
    ) -> list[tuple[MOBase | Termination, Verb]]:
        """
        for Address and Engagement objects:
            Loops through the objects, and sets the uuid if an existing matching object
            is found
        for ITUser objects:
            Loops through the objects and removes it if an existing matchin object is
            found
        for all other objects:
            returns the input list of converted_objects
        """
        # We can't infer the type from json_key because of Terminate objects
        mo_class = one({type(o) for o in converted_objects})

        if issubclass(mo_class, Termination):
            return [(obj, Verb.TERMINATE) for obj in converted_objects]

        converted_objects = cast(Sequence[MOBase], converted_objects)

        mapping = await self.construct_uuid_mapping(converted_objects)

        # Partition the mapping into creates and updates
        creates, updates = partition(
            # We have an update if there is no MO object in the mapping
            star(lambda converted, mo_object: mo_object is not None),
            mapping,
        )
        updates = cast(Iterator[tuple[MOBase, MOBase]], updates)

        # Convert creates to operations
        operations: list[tuple[MOBase | Termination, Verb]] = [
            (converted_object, Verb.CREATE) for converted_object, _ in creates
        ]

        # Convert updates to operations
        for converted_object, matching_object in updates:
            # Convert our objects to dicts
            mo_object_dict_to_upload = matching_object.dict()
            # Need to by_alias=True to extract the terminate_ field as its alias,
            # _terminate_. Only the *intersection* of attribute names from
            # mo_object_dict_to_upload and converted_mo_object_dict are used.
            converted_mo_object_dict = converted_object.dict(by_alias=True)

            # Update the existing MO object with the converted values
            # NOTE: UUID cannot be updated as it is used to decide what we update
            # NOTE: objectClass is removed as it is an LDAP implemenation detail
            # TODO: Why do we not update validity???
            mo_attributes = mo_attributes - {"validity", "uuid", "objectClass"}
            # Only copy over keys that exist in both sets
            mo_attributes = mo_attributes & converted_mo_object_dict.keys()

            update_values = {
                key: converted_mo_object_dict[key] for key in mo_attributes
            }
            logger.info(
                "Setting values on upload dict",
                uuid=mo_object_dict_to_upload["uuid"],
                values=update_values,
            )

            mo_object_dict_to_upload.update(update_values)
            converted_object_uuid_checked = mo_class(**mo_object_dict_to_upload)

            # If an object is identical to the one already there, it does not need
            # to be uploaded.
            if converted_object_uuid_checked == matching_object:
                logger.info(
                    "Converted object is identical to existing object, skipping"
                )
                continue
            # We found a match, so we are editing the object we matched
            operations.append((converted_object_uuid_checked, Verb.EDIT))

        return operations

    @wait_for_import_to_finish
    @with_exitstack
    async def import_single_user(self, dn: DN, exit_stack: ExitStack) -> None:
        """Imports a single user from LDAP into MO.

        Args:
            dn: The DN that triggered our event changed in LDAP.
        """
        exit_stack.enter_context(bound_contextvars(dn=dn))

        logger.info("Importing user")

        if not self.settings.conversion_mapping.ldap_to_mo:
            logger.info("import_single_user called without mapping")
            return

        # Get the employee's UUID (if they exists)
        employee_uuid = await self.dataloader.find_mo_employee_uuid(dn)
        if employee_uuid:
            # If we found an employee UUID, we want to use that to find all DNs
            dns = await self.dataloader.find_mo_employee_dn(employee_uuid)
        else:  # We did not find an employee UUID
            ldap_to_mo = self.settings.conversion_mapping.ldap_to_mo
            assert ldap_to_mo is not None
            # Check if we wish to create the employee or not
            if "Employee" not in ldap_to_mo:  # pragma: no cover
                logger.info(
                    "Employee not found in MO, and no ldap_to_mo Employee mapping"
                )
                return
            employee_mapping = ldap_to_mo["Employee"]

            create_employee = employee_mapping.import_to_mo == "true"
            if not create_employee:
                # If we do not want to create the employee and it does not exist, there
                # is no more to be done, as we cannot create dependent resources with no
                # employee to attach them to.
                logger.info("Employee not found in MO, and not configured to create it")
                return
            logger.info("Employee not found, but configured to create it")

            # As we wish to create an employee, we need to generate an UUID for it
            employee_uuid = EmployeeUUID(uuid4())
            logger.info(
                "Employee not found in MO, generated UUID", employee_uuid=employee_uuid
            )
            # At this point employee_uuid is always set

            # We want to create our employee using the best possible LDAP account.
            # By default, we will use the account that was provided to us in the event.
            dns = {dn}

            # However we may be able to find other accounts using the CPR number on the
            # event triggered account, by searching for the CPR number in all of LDAP.
            # Note however, that this will only succeed if there is a CPR number field.
            cpr_number = await self.dataloader.ldapapi.dn2cpr(dn)
            # Only attempt to load accounts if we have a CPR number to do so with
            if cpr_number:
                dns = await self.dataloader.ldapapi.cpr2dns(cpr_number)

        # At this point 'employee_uuid' is an UUID that may or may not be in MO
        # At this point 'dns' is a list of LDAP account DNs

        # We always want to synchronize from the best LDAP account, instead of just
        # synchronizing from the last LDAP account that has been touched.
        # Thus we process the list of DNs found for the user to pick the best one.
        dns = await filter_dns(self.settings, self.ldap_connection, dns)
        best_dn = await apply_discriminator(self.settings, self.ldap_connection, dns)
        # If no good LDAP account was found, we do not want to synchronize at all
        if best_dn is None:
            logger.info(
                "Aborting synchronization, as no good LDAP account was found",
                dns=dns,
                employee_uuid=employee_uuid,
            )
            return

        # At this point, we have the best possible DN for the user, and their employee UUID
        if dn != best_dn:
            logger.info(
                "Found better DN for employee",
                best_dn=best_dn,
                dns=dns,
                employee_uuid=employee_uuid,
            )
        dn = best_dn
        exit_stack.enter_context(bound_contextvars(dn=dn))

        json_keys = set(self.settings.conversion_mapping.ldap_to_mo.keys())
        json_keys = {
            json_key
            for json_key in json_keys
            if self.settings.conversion_mapping.ldap_to_mo[json_key].import_to_mo
            != "false"
        }
        logger.info("Import to MO filtered", json_keys=json_keys)

        json_keys = {
            json_key
            for json_key in json_keys
            if await self.perform_import_checks(dn, json_key)
        }
        logger.info("Import checks executed", json_keys=json_keys)

        template_context = {
            "employee_uuid": str(employee_uuid),
        }

        # First import the Employee, then Engagement if present, then the rest.
        # We want this order so dependencies exist before their dependent objects
        if "Employee" in json_keys:
            await self.import_single_entity(
                self.get_mapping("Employee"), dn, template_context
            )
            json_keys.discard("Employee")

        if "Engagement" in json_keys:
            await self.import_single_entity(
                self.get_mapping("Engagement"), dn, template_context
            )
            json_keys.discard("Engagement")

        await asyncio.gather(
            *[
                self.import_single_entity(
                    self.get_mapping(json_key), dn, template_context
                )
                for json_key in json_keys
            ]
        )

    async def import_single_entity(
        self,
        mapping: LDAP2MOMapping,
        dn: str,
        template_context: dict[str, Any],
    ) -> None:
        logger.info("Loading object", mo_class=mapping.as_mo_class(), dn=dn)
        loaded_object = await get_ldap_object(
            ldap_connection=self.ldap_connection,
            dn=dn,
            attributes=set(mapping.ldap_attributes) - {"dn"},
        )
        logger.info(
            "Loaded object",
            mo_class=mapping.as_mo_class(),
            dn=dn,
            loaded_object=loaded_object,
        )

        try:
            converted_objects = await self.converter.from_ldap(
                ldap_object=loaded_object,
                mapping=mapping,
                template_context=template_context,
            )
        except SkipObject:
            logger.info("Skipping object", dn=dn)
            return

        if not converted_objects:
            logger.info("No converted objects", dn=dn)
            return

        logger.info(
            "Converted 'n' objects ",
            n=len(converted_objects),
            dn=dn,
        )
        if mapping.objectClass == "Custom.JobTitleFromADToMO":  # pragma: no cover
            assert all(isinstance(obj, JobTitleFromADToMO) for obj in converted_objects)
            custom_objects = cast(list[JobTitleFromADToMO], converted_objects)

            await asyncio.gather(
                *[
                    obj.sync_to_mo(self.dataloader.moapi.graphql_client)
                    for obj in custom_objects
                ]
            )
            return

        mo_attributes = set(mapping.get_fields().keys())
        operations = await self.format_converted_objects(
            converted_objects, mo_attributes
        )
        if not operations:  # pragma: no cover
            logger.info("No converted objects after formatting", dn=dn)
            return

        logger.info(
            "Importing objects",
            operations=operations,
            dn=dn,
        )
        await self.dataloader.moapi.create_or_edit_mo_objects(operations)
