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
from fastramqpi.ramqp.utils import RequeueMessage
from ldap3 import Connection
from more_itertools import all_equal
from more_itertools import duplicates_everseen
from more_itertools import first
from more_itertools import one
from more_itertools import only
from more_itertools import partition
from more_itertools import quantify
from structlog.contextvars import bound_contextvars

from .config import Settings
from .converters import LdapConverter
from .customer_specific_checks import ExportChecks
from .customer_specific_checks import ImportChecks
from .dataloaders import DN
from .dataloaders import DataLoader
from .exceptions import DNNotFound
from .exceptions import SkipObject
from .ldap import apply_discriminator
from .ldap import get_ldap_object
from .moapi import Verb
from .models import Address
from .models import Employee
from .models import Engagement
from .models import ITUser
from .models import MOBase
from .types import EmployeeUUID
from .types import OrgUnitUUID
from .utils import bucketdict
from .utils import ensure_list
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
        if self.settings.check_holstebro_ou_issue_57426:
            return await self.import_checks.check_holstebro_ou_is_externals_issue_57426(
                self.settings.check_holstebro_ou_issue_57426,
                dn,
                json_key,
            )
        return True

    async def _find_best_dn(
        self, uuid: EmployeeUUID, dry_run: bool = False
    ) -> tuple[DN | None, bool]:
        dns = await self.dataloader.find_mo_employee_dn(uuid)
        # If we found DNs, we want to synchronize to the best of them
        if dns:
            logger.info("Found DNs for user", dns=dns, uuid=uuid)
            best_dn = await apply_discriminator(
                self.settings, self.ldap_connection, dns
            )
            # If no good LDAP account was found, we do not want to synchronize at all
            if best_dn:
                return best_dn, False
            logger.warning(
                "Aborting synchronization, as no good LDAP account was found",
                dns=dns,
                uuid=uuid,
            )
            return None, False

        # If dry-running we do not want to generate real DNs in LDAP
        if dry_run:
            return "CN=Dry run,DC=example,DC=com", True

        if not self.settings.add_objects_to_ldap:
            logger.info(
                "Aborting synchronization, as no LDAP account was found and we are not configured to create",
                uuid=uuid,
            )
            return None, True

        # If we did not find DNs, we want to make one
        try:
            # This call actually writes in LDAP, so make sure that is okay
            # TODO: Restructure the code so it does not actually write
            await self.perform_export_checks(uuid)
            best_dn = await self.dataloader.make_mo_employee_dn(uuid)
        except DNNotFound as error:
            # If this occurs we were unable to generate a DN for the user
            logger.error("Unable to generate DN")
            raise RequeueMessage("Unable to generate DN") from error
        return best_dn, True

    async def render_ldap2mo(self, uuid: EmployeeUUID, dn: DN) -> dict[str, list[Any]]:
        await self.perform_export_checks(uuid)

        mo2ldap_template = self.settings.conversion_mapping.mo2ldap
        assert mo2ldap_template is not None
        template = self.converter.environment.from_string(mo2ldap_template)
        result = await template.render_async({"uuid": uuid, "dn": dn})
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert all(isinstance(key, str) for key in parsed)
        # TODO: force users to configure as list instead of implicitly
        # converting (very confusing).
        # assert all(isinstance(value, list) for value in parsed.values())
        return {key: ensure_list(value) for key, value in parsed.items()}

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

        best_dn, create = await self._find_best_dn(uuid, dry_run=dry_run)
        if best_dn is None:
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
        else:
            await self.dataloader.ldapapi.modify_ldap_object(
                best_dn, ldap_desired_state
            )

        return ldap_desired_state

    async def format_converted_objects(
        self,
        converted_objects: Sequence[MOBase],
        json_key: str,
    ) -> list[tuple[MOBase, Verb]]:
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
        objects_in_mo: Sequence[MOBase]

        # Load addresses already in MO
        if issubclass(mo_class, Address):
            converted_objects = cast(Sequence[Address], converted_objects)

            assert all_equal([obj.person for obj in converted_objects])
            person = first(converted_objects).person

            assert all_equal([obj.org_unit for obj in converted_objects])
            org_unit = first(converted_objects).org_unit

            assert all_equal([obj.address_type for obj in converted_objects])
            address_type = first(converted_objects).address_type

            if person:
                objects_in_mo = await self.dataloader.moapi.load_mo_employee_addresses(
                    person,
                    address_type,
                )
            elif org_unit:
                objects_in_mo = await self.dataloader.moapi.load_mo_org_unit_addresses(
                    OrgUnitUUID(org_unit),
                    address_type,
                )
            else:
                logger.info(
                    "Could not format converted "
                    "objects: An address needs to have either a person uuid "
                    "OR an org unit uuid"
                )
                return []

            # TODO: It seems weird to match addresses by value, as value is likely to
            #       change quite often. Omada simply deletes and recreates addresses.
            #       Maybe we should consider doing the same here?
            value_key = "value"

        # Load engagements already in MO
        elif issubclass(mo_class, Engagement):
            converted_objects = cast(Sequence[Engagement], converted_objects)

            assert all_equal([obj.person for obj in converted_objects])
            person = first(converted_objects).person

            objects_in_mo = await self.dataloader.moapi.load_mo_employee_engagements(
                person
            )
            value_key = "user_key"
            user_keys = [o.user_key for o in objects_in_mo]

            # If we have duplicate user_keys, remove those which are the same as the
            # primary engagement's user_key
            duplicate_user_keys = duplicates_everseen(user_keys)
            if any(duplicate_user_keys):
                primaries = await self.dataloader.moapi.is_primaries(
                    [o.uuid for o in objects_in_mo]
                )
                num_primaries = quantify(primaries)
                if num_primaries > 1:
                    raise RequeueMessage(
                        "Waiting for multiple primary engagements to be resolved"
                    )
                # TODO: if num_primaries == 0, we cannot remove duplicates, is this a problem?

                if num_primaries == 1:
                    primary_engagement = objects_in_mo[primaries.index(True)]
                    logger.info(
                        "Found primary engagement",
                        uuid=str(primary_engagement.uuid),
                        user_key=primary_engagement.user_key,
                    )
                    logger.info("Removing engagements with identical user keys")
                    objects_in_mo = [
                        o
                        for o in objects_in_mo
                        # Keep the primary engagement itself
                        if o == primary_engagement
                        # But remove duplicate user-key engagements
                        or o.user_key != primary_engagement.user_key
                    ]

        elif issubclass(mo_class, ITUser):
            converted_objects = cast(Sequence[ITUser], converted_objects)

            assert all_equal([obj.person for obj in converted_objects])
            person = first(converted_objects).person
            assert person is not None

            assert all_equal([obj.itsystem for obj in converted_objects])
            itsystem = first(converted_objects).itsystem

            objects_in_mo = await self.dataloader.moapi.load_mo_employee_it_users(
                person, itsystem
            )

            value_key = "user_key"
        elif issubclass(mo_class, Employee):
            converted_objects = cast(Sequence[Employee], converted_objects)

            # GraphQL employee_create actually updates if the employee already exists,
            # using validity from the CPR-number like with creates. We need to use this
            # undocumented feature of the GraphQL API to avoid calculating the validity
            # manually based on the CPR-number, since we are not passed an explicit
            # validity through the legacy ramodels employee object.
            # TODO: don't short-circuit when we receive an employee object with proper
            # validity.
            return [
                (converted_object, Verb.CREATE)
                for converted_object in converted_objects
            ]
        else:  # pragma: no cover
            raise AssertionError(f"Unknown mo_class: {mo_class}")

        mapper_template = self.converter.mapping["ldap_to_mo"][json_key].get(
            "_mapper_", None
        )
        if mapper_template is not None:
            mo_values_task = asyncio.gather(
                *[mapper_template.render_async({"obj": obj}) for obj in objects_in_mo]
            )
            ldap_values_task = asyncio.gather(
                *[
                    mapper_template.render_async({"obj": obj})
                    for obj in converted_objects
                ]
            )
            mo_values, ldap_values = await asyncio.gather(
                mo_values_task, ldap_values_task
            )
            mo_mapper = dict(zip(objects_in_mo, mo_values, strict=False))
            ldap_mapper = dict(zip(converted_objects, ldap_values, strict=False))
        else:
            # TODO: Refactor so this is handled using default templates instead
            mo_mapper = {obj: getattr(obj, value_key) for obj in objects_in_mo}
            ldap_mapper = {obj: getattr(obj, value_key) for obj in converted_objects}

        # Construct a map from value-key to list of matching objects
        values_in_mo = bucketdict(objects_in_mo, mo_mapper.get)
        values_converted = bucketdict(converted_objects, ldap_mapper.get)

        # Only values in MO targeted by our converted values are relevant
        values_in_mo = {
            key: value for key, value in values_in_mo.items() if key in values_converted
        }

        # We need a mapping between MO objects and converted objects.
        # Without a mapping we cannot maintain temporality of objects in MO.

        # If we have more than one MO object for each converted, the match is ambiguous.
        # Ambiguous matches mean no mapping and must be handled by human intervention.
        ambiguous_exception = RequeueMessage(
            f"Bad mapping: Multiple MO objects for {json_key}"
        )
        value_in_mo = {
            key: only(value, too_long=ambiguous_exception)
            for key, value in values_in_mo.items()
        }

        # If we have more than one converted per value-key there cannot be a mapping.
        # This probably means we have a misconfiguration of the integration.
        # Perhaps a bad discriminator between MO objects per converted object.
        bad_discriminator_exception = RequeueMessage(
            f"Bad mapping: Multiple converted for {json_key}"
        )
        value_converted = {
            key: one(value, too_long=bad_discriminator_exception)
            for key, value in values_converted.items()
        }

        # At this point we know a mapping exists from converted objects to MO objects
        mapping = [
            (value_converted[key], value_in_mo.get(key)) for key in value_converted
        ]

        # Partition the mapping into creates and updates
        creates, updates = partition(
            # We have an update if there is no MO object in the mapping
            star(lambda converted, mo_object: mo_object is not None),
            mapping,
        )
        updates = cast(Iterator[tuple[MOBase, MOBase]], updates)

        # Convert creates to operations
        operations = [
            (converted_object, Verb.CREATE) for converted_object, _ in creates
        ]

        # Convert updates to operations
        mo_attributes = set(self.converter.get_mo_attributes(json_key))
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

            # TODO: Try to get this reactivated, see: 87683a2b
            # # If an object is identical to the one already there, it does not need
            # # to be uploaded.
            # if converted_object_uuid_checked == matching_object:
            #     logger.info(
            #         "Converted object is identical "
            #         "to existing object, skipping"
            #     )
            #     continue
            # We found a match, so we are editing the object we matched
            operations.append((converted_object_uuid_checked, Verb.EDIT))

        return operations

    @wait_for_import_to_finish
    @with_exitstack
    async def import_single_user(
        self, dn: DN, exit_stack: ExitStack, manual_import: bool = False
    ) -> None:
        """Imports a single user from LDAP into MO.

        Args:
            dn: The DN that triggered our event changed in LDAP.
            manual_import: Whether this import operation was manually triggered.
        """
        exit_stack.enter_context(bound_contextvars(dn=dn, manual_import=manual_import))

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
            # Check if we wish to create the employee or not
            create_employee = False
            if (
                ldap_to_mo
                and "Employee" in ldap_to_mo
                and ldap_to_mo["Employee"].import_to_mo_as_bool(manual_import)
            ):
                create_employee = True
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
            if self.settings.conversion_mapping.ldap_to_mo[
                json_key
            ].import_to_mo_as_bool(manual_import)
        }
        logger.info("Import to MO filtered", json_keys=json_keys)

        json_keys = {
            json_key
            for json_key in json_keys
            if await self.perform_import_checks(dn, json_key)
        }
        logger.info("Import checks executed", json_keys=json_keys)

        # First import the Employee, then Engagement if present, then the rest.
        # We want this order so dependencies exist before their dependent objects
        if "Employee" in json_keys:
            await self.import_single_user_entity("Employee", dn, employee_uuid)
            json_keys.discard("Employee")

        if "Engagement" in json_keys:
            await self.import_single_user_entity("Engagement", dn, employee_uuid)
            json_keys.discard("Engagement")

        await asyncio.gather(
            *[
                self.import_single_user_entity(json_key, dn, employee_uuid)
                for json_key in json_keys
            ]
        )

    async def import_single_user_entity(
        self, json_key: str, dn: str, employee_uuid: UUID
    ) -> None:
        logger.info("Loading object", dn=dn, json_key=json_key)
        loaded_object = await get_ldap_object(
            self.ldap_connection, dn, self.converter.get_ldap_attributes(json_key)
        )
        logger.info(
            "Loaded object",
            dn=dn,
            json_key=json_key,
            loaded_object=loaded_object,
        )

        try:
            converted_objects = await self.converter.from_ldap(
                loaded_object,
                json_key,
                employee_uuid=employee_uuid,
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
        if json_key == "Custom":
            await asyncio.gather(
                *[
                    obj.sync_to_mo(self.dataloader.graphql_client)
                    for obj in converted_objects
                ]
            )
            return

        converted_objects = await self.format_converted_objects(
            converted_objects, json_key
        )
        if not converted_objects:  # pragma: no cover
            logger.info("No converted objects after formatting", dn=dn)
            return

        logger.info(
            "Importing objects",
            converted_objects=converted_objects,
            dn=dn,
        )
        await self.dataloader.moapi.create_or_edit_mo_objects(converted_objects)
