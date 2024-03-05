# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""
Created on Fri Mar  3 09:46:15 2023

@author: nick
"""
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastramqpi.context import Context
from httpx import HTTPStatusError
from ramodels.mo import MOBase
from ramodels.mo.details import ITUser
from ramqp.depends import handle_exclusively_decorator
from ramqp.mo import MORoutingKey

from .dataloaders import DNList
from .dataloaders import Verb
from .exceptions import DNNotFound
from .exceptions import IgnoreChanges
from .exceptions import NoObjectsReturnedException
from .exceptions import NotSupportedException
from .ldap import cleanup
from .ldap_classes import LdapObject
from .logging import logger
from .utils import extract_ou_from_dn
from .utils import get_object_type_from_routing_key


class IgnoreMe:
    def __init__(self):
        self.ignore_dict: dict[str, list[datetime]] = {}

    def __getitem__(self, key: str | UUID) -> list[datetime]:
        key = self.format_entry(key)
        return self.ignore_dict.get(key, [])

    def __len__(self):
        return len(self.ignore_dict)

    def format_entry(self, entry: str | UUID) -> str:
        if not isinstance(entry, str):
            entry = str(entry)
        return entry.lower()

    def clean(self):
        # Remove all timestamps which have been in the ignore dict for more than 60 sec.
        now = datetime.now()
        max_age = 60  # seconds
        cutoff = now - timedelta(seconds=max_age)
        for str_to_ignore, timestamps in self.ignore_dict.items():
            for timestamp in timestamps.copy():
                if timestamp < cutoff:
                    logger.info(
                        "[clean-ignore-dict] Removing entry from ignore-dict.",
                        timestamp=timestamp,
                        str_to_ignore=str_to_ignore,
                        max_age=max_age,
                    )
                    timestamps.remove(timestamp)

        # Remove keys with empty lists
        self.ignore_dict = {k: v for k, v in self.ignore_dict.items() if v}

    def add(self, str_to_add: str | UUID):
        # Add a string to the ignore dict
        str_to_add = self.format_entry(str_to_add)

        if str_to_add in self.ignore_dict:
            self.ignore_dict[str_to_add].append(datetime.now())
        else:
            self.ignore_dict[str_to_add] = [datetime.now()]

    def remove(self, str_to_remove: str | UUID):
        str_to_remove = self.format_entry(str_to_remove)

        if str_to_remove in self.ignore_dict:
            # Remove latest entry from the ignore dict
            newest_timestamp = max(self.ignore_dict[str_to_remove])
            self.ignore_dict[str_to_remove].remove(newest_timestamp)

    def check(self, str_to_check: str | UUID):
        # Raise ignoreChanges if the string to check is in self.ignore_dict
        str_to_check = self.format_entry(str_to_check)
        self.clean()

        if str_to_check in self.ignore_dict and self.ignore_dict[str_to_check]:
            # Remove timestamp so it does not get ignored twice.
            oldest_timestamp = min(self.ignore_dict[str_to_check])
            self.ignore_dict[str_to_check].remove(oldest_timestamp)
            raise IgnoreChanges(f"[Check-ignore-dict] Ignoring {str_to_check}")


class SyncTool:
    def __init__(self, context: Context):
        # UUIDs in this list will be ignored by listen_to_changes ONCE
        self.uuids_to_ignore = IgnoreMe()
        self.dns_to_ignore = IgnoreMe()

        self.context = context
        self.user_context = self.context["user_context"]
        self.dataloader = self.user_context["dataloader"]
        self.converter = self.user_context["converter"]
        self.export_checks = self.user_context["export_checks"]
        self.import_checks = self.user_context["import_checks"]
        self.settings = self.user_context["settings"]
        self.internal_amqpsystem = self.user_context["internal_amqpsystem"]

    @staticmethod
    def wait_for_export_to_finish(func: Callable):
        """Runs the function while ensuring sequentiality w.r.t. the uuid parameter."""

        def extract_uuid(obj) -> UUID:
            """
            Extract an uuid from an object and return it

            Parameters
            -------------
            obj: Any
                Object which is either an uuid or an object with an uuid attribute
            """
            uuid = getattr(obj, "uuid", obj)
            if not isinstance(uuid, UUID):
                raise TypeError(f"{uuid} is not an uuid")
            return uuid

        def uuid_extractor(self, *args, **kwargs) -> UUID:
            uuid = extract_uuid(args[0] if args else kwargs["uuid"])
            logger.info("[Wait-for-export-to-finish] Generating UUID.", uuid=str(uuid))
            return uuid

        return handle_exclusively_decorator(uuid_extractor)(func)

    @staticmethod
    def wait_for_import_to_finish(func: Callable):
        """Runs the function while ensuring sequentiality w.r.t. the dn parameter."""

        def dn_extractor(self, *args, **kwargs):
            dn = args[0] if args else kwargs["dn"]
            logger.info("[Wait-for-import-to-finish] Generating DN.", dn=dn)
            return dn

        return handle_exclusively_decorator(dn_extractor)(func)

    async def perform_export_checks(self, employee_uuid: UUID, object_uuid: UUID):
        """
        Perform a number of customer-specific checks. Raising IgnoreChanges() if a
        check fails
        """

        if self.settings.check_alleroed_sd_number:
            # Check that an SD-employee number does not start with 9
            # If it does, rejectMessage is raised.
            await self.export_checks.check_alleroed_sd_number(
                employee_uuid,
                object_uuid,
            )

        # Check that the employee has an it-user with user_key = it_user_to_check
        await self.export_checks.check_it_user(
            employee_uuid,
            self.settings.it_user_to_check,
        )

    async def perform_import_checks(self, dn: str, json_key: str):
        if self.settings.check_holstebro_ou_issue_57426:
            await self.import_checks.check_holstebro_ou_is_externals_issue_57426(
                self.settings.check_holstebro_ou_issue_57426,
                dn,
                json_key,
            )

    def cleanup_needed(self, ldap_modify_responses: list[dict]):
        """
        If nothing was modified in LDAP, we also do not need to clean up.
        """
        for response in ldap_modify_responses:
            if response and response["description"] == "success":
                return True

        logger.info("[Cleanup-needed] No cleanup needed")
        return False

    def move_ldap_object(self, ldap_object: LdapObject, dn: str) -> LdapObject:
        """
        Parameters
        ----------------
        ldap_object: LdapObject
            LDAP object as converted by converter.to_ldap()
        dn: str
            DN which we expect the object to have

        Notes
        -----------
        If the DN on the ldap object is different from the supplied dn, we move the
        object in LDAP, so the two match. We always assume that the DN on the LDAP
        object is correct, because that one is mapped in the json file.
        """
        old_dn = dn
        new_dn = ldap_object.dn

        if new_dn == old_dn:
            return ldap_object

        old_ou = extract_ou_from_dn(old_dn)
        new_ou = extract_ou_from_dn(new_dn)

        logger.info(
            "[Move-LDAP-object] Moving user to new organizational unit.",
            old_ou=old_ou,
            new_ou=new_ou,
            old_dn=old_dn,
            new_dn=new_dn,
        )

        # Create the new OU (dataloader.create_ou checks if it exists)
        self.dataloader.create_ou(new_ou)

        # Move the object to the proper OU
        move_successful: bool = self.dataloader.move_ldap_object(old_dn, new_dn)

        if move_successful:
            # Delete the old OU (dataloader.delete_ou checks if it is empty)
            self.dataloader.delete_ou(old_ou)
        else:
            ldap_object.dn = old_dn

        return ldap_object

    @wait_for_export_to_finish
    async def listen_to_changes_in_employees(
        self,
        uuid: UUID,
        object_uuid: UUID,
        routing_key: MORoutingKey,
        delete: bool,
        current_objects_only: bool,
    ) -> None:
        """
        Parameters
        ---------------
        uuid: UUID
            uuid of the changed employee
        object_uuid: UUID
            uuid of the changed object, belonging to the changed employee
        routing_key: MoRoutingKey
            Routing key of the AMQP message
        delete: bool
            Whether to delete the object or not
        current_objects_only: bool
            Whether to load currently valid objects only or not
        """
        logger_args = {
            "uuid": str(uuid),
            "object_uuid": str(object_uuid),
            "routing_key": routing_key,
            "delete": delete,
        }

        logger.info(
            "[Listen-to-changes-in-employees] Registered change in an employee.",
            **logger_args,
        )

        # If the object was uploaded by us, it does not need to be synchronized.
        # Note that this is not necessary in listen_to_changes_in_org_units. Because
        # those changes potentially map to multiple employees
        try:
            self.uuids_to_ignore.check(object_uuid)
        except IgnoreChanges as e:
            logger.info("[Listen-to-changes-in-employees] " + str(e))
            return
        await self.perform_export_checks(uuid, object_uuid)

        try:
            dns: DNList = await self.dataloader.find_or_make_mo_employee_dn(uuid)
        except DNNotFound:
            logger.info("[Listen-to-changes-in-employees] DN not found.", **logger_args)
            return

        # Get MO employee
        changed_employee = await self.dataloader.load_mo_employee(
            uuid,
            current_objects_only=current_objects_only,
        )
        logger.info(
            "[Listen-to-changes-in-employees] Found Employee in MO.",
            changed_employee=changed_employee,
            **logger_args,
        )

        mo_object_dict: dict[str, Any] = {"mo_employee": changed_employee}
        object_type = get_object_type_from_routing_key(routing_key)

        if object_type == "person":
            for dn in dns:
                # Convert to LDAP
                ldap_employee = await self.converter.to_ldap(
                    mo_object_dict, "Employee", dn
                )
                ldap_employee = self.move_ldap_object(ldap_employee, dn)

                # Upload to LDAP - overwrite because all employee fields are unique.
                # One person cannot have multiple names.
                await self.dataloader.modify_ldap_object(
                    ldap_employee,
                    "Employee",
                    overwrite=True,
                    delete=delete,
                )

        elif object_type == "address":
            # Get MO address
            changed_address = await self.dataloader.load_mo_address(
                object_uuid,
                current_objects_only=current_objects_only,
            )
            address_type_uuid = str(changed_address.address_type.uuid)
            json_key = await self.converter.get_employee_address_type_user_key(
                address_type_uuid
            )

            logger.info(
                "[Listen-to-changes-in-employees] Obtained address.",
                user_key=json_key,
                **logger_args,
            )
            mo_object_dict["mo_employee_address"] = changed_address

            # Convert & Upload to LDAP
            affected_dn = await self.dataloader.find_dn_by_engagement_uuid(
                uuid, changed_address.engagement, dns
            )
            ldap_object = await self.converter.to_ldap(
                mo_object_dict, json_key, affected_dn
            )
            ldap_object = self.move_ldap_object(ldap_object, affected_dn)

            ldap_modify_responses = await self.dataloader.modify_ldap_object(
                ldap_object,
                json_key,
                delete=delete,
            )

            if self.cleanup_needed(ldap_modify_responses):
                addresses_in_mo = await self.dataloader.load_mo_employee_addresses(
                    changed_employee.uuid, changed_address.address_type.uuid
                )

                await cleanup(
                    json_key,
                    "mo_employee_address",
                    addresses_in_mo,
                    self.user_context,
                    changed_employee,
                    object_type,
                    ldap_object.dn,
                )

        elif object_type == "ituser":
            # Get MO IT-user
            changed_it_user = await self.dataloader.load_mo_it_user(
                object_uuid,
                current_objects_only=current_objects_only,
            )
            it_system_type_uuid = changed_it_user.itsystem.uuid
            json_key = await self.converter.get_it_system_user_key(it_system_type_uuid)

            logger.info(
                "[Listen-to-changes-in-employees] Obtained IT system.",
                user_key=json_key,
                **logger_args,
            )
            mo_object_dict["mo_employee_it_user"] = changed_it_user

            # Convert & Upload to LDAP
            affected_dn = await self.dataloader.find_dn_by_engagement_uuid(
                uuid, changed_it_user.engagement, dns
            )
            ldap_object = await self.converter.to_ldap(
                mo_object_dict, json_key, affected_dn
            )
            ldap_object = self.move_ldap_object(ldap_object, affected_dn)

            ldap_modify_responses = await self.dataloader.modify_ldap_object(
                ldap_object,
                json_key,
                delete=delete,
            )

            if self.cleanup_needed(ldap_modify_responses):
                # Load IT users belonging to this employee
                it_users_in_mo = await self.dataloader.load_mo_employee_it_users(
                    changed_employee.uuid, it_system_type_uuid
                )

                await cleanup(
                    json_key,
                    "mo_employee_it_user",
                    it_users_in_mo,
                    self.user_context,
                    changed_employee,
                    object_type,
                    ldap_object.dn,
                )

        elif object_type == "engagement":
            # Get MO Engagement
            changed_engagement = await self.dataloader.load_mo_engagement(
                object_uuid,
                current_objects_only=current_objects_only,
            )

            json_key = "Engagement"
            mo_object_dict["mo_employee_engagement"] = changed_engagement

            # Convert & Upload to LDAP
            # We upload an engagement to LDAP regardless of its 'primary' attribute.
            # Because it looks like you cannot set 'primary' when creating an engagement
            # in the OS2mo GUI.
            affected_dn = await self.dataloader.find_dn_by_engagement_uuid(
                uuid, changed_engagement, dns
            )
            ldap_object = await self.converter.to_ldap(
                mo_object_dict, json_key, affected_dn
            )
            ldap_object = self.move_ldap_object(ldap_object, affected_dn)
            ldap_modify_responses = await self.dataloader.modify_ldap_object(
                ldap_object,
                json_key,
                delete=delete,
            )

            if self.cleanup_needed(ldap_modify_responses):
                engagements_in_mo = await self.dataloader.load_mo_employee_engagements(
                    changed_employee.uuid
                )

                await cleanup(
                    json_key,
                    "mo_employee_engagement",
                    engagements_in_mo,
                    self.user_context,
                    changed_employee,
                    object_type,
                    ldap_object.dn,
                )

    @wait_for_export_to_finish
    async def process_employee_address(
        self,
        affected_employee,
        org_unit_uuid,
        changed_address,
        json_key,
        delete,
        object_type,
    ):
        await self.perform_export_checks(affected_employee.uuid, changed_address.uuid)
        dns: DNList = await self.dataloader.find_or_make_mo_employee_dn(
            affected_employee.uuid
        )

        mo_object_dict = {
            "mo_employee": affected_employee,
            "mo_org_unit_address": changed_address,
        }

        for dn in dns:
            # Convert & Upload to LDAP
            ldap_object = await self.converter.to_ldap(mo_object_dict, json_key, dn)
            ldap_object = self.move_ldap_object(ldap_object, dn)

            ldap_modify_responses = await self.dataloader.modify_ldap_object(
                ldap_object,
                json_key,
                delete=delete,
            )

            if self.cleanup_needed(ldap_modify_responses):
                addresses_in_mo = await self.dataloader.load_mo_org_unit_addresses(
                    org_unit_uuid, changed_address.address_type.uuid
                )

                await cleanup(
                    json_key,
                    "mo_org_unit_address",
                    addresses_in_mo,
                    self.user_context,
                    affected_employee,
                    object_type,
                    ldap_object.dn,
                )

    async def publish_engagements_for_org_unit(self, org_unit_uuid: UUID) -> None:
        """
        Loops through all employees who are connected to an org-unit and publishes
        'engagement' AMQP messages for all of them.

        Parameters
        -------------
        org_unit_uuid : UUId
            UUID of the org-unit for which to publish messages
        """
        employees = await self.dataloader.load_mo_employees_in_org_unit(org_unit_uuid)
        for employee in employees:
            engagements = await self.dataloader.load_mo_employee_engagements(
                employee.uuid
            )

            for engagement in engagements:
                if engagement.org_unit.uuid == org_unit_uuid:
                    await self.refresh_object(engagement.uuid, "engagement")

    @wait_for_export_to_finish
    async def listen_to_changes_in_org_units(
        self,
        uuid: UUID,
        object_uuid: UUID,
        routing_key: MORoutingKey,
        delete: bool,
        current_objects_only: bool,
    ) -> None:
        """
        Parameters
        ---------------
        uuid: UUID
            uuid of the changed org-unit
        object_uuid: UUID
            uuid of the changed object, belonging to the changed org-unit
        routing_key: MoRoutingKey
            Routing key of the AMQP message
        delete: bool
            Whether to delete the object or not
        current_objects_only: bool
            Whether to load currently valid objects only or not
        """

        logger_args = {
            "uuid": str(uuid),
            "object_uuid": str(object_uuid),
            "routing_key": routing_key,
            "delete": delete,
        }

        logger.info(
            "[Listen-to-changes-in-orgs] Registered change in an org_unit.",
            current_objects_only=current_objects_only,
            **logger_args,
        )

        # When an org-unit is changed we need to update the org unit info. So we
        # know the new name of the org unit in case it was changed
        object_type = get_object_type_from_routing_key(routing_key)
        if object_type == "org_unit":
            logger.info(
                "[Listen-to-changes-in-orgs] Updating org unit info.", **logger_args
            )
            self.converter.org_unit_info = await self.dataloader.load_mo_org_units()
            self.converter.check_org_unit_info_dict()

            # In case the name of the org-unit changed, we need to publish an
            # "engagement" message for each of its employees. Because org-unit
            # LDAP mapping is primarily done through the "Engagment" json-key.
            await self.publish_engagements_for_org_unit(object_uuid)

        if object_type == "address":
            # Get MO address
            changed_address = await self.dataloader.load_mo_address(
                object_uuid,
                current_objects_only=current_objects_only,
            )
            address_type_uuid = str(changed_address.address_type.uuid)
            json_key = await self.converter.get_org_unit_address_type_user_key(
                address_type_uuid
            )

            logger.info(
                "[Listen-to-changes-in-orgs] Obtained address.",
                user_key=json_key,
                **logger_args,
            )

            ldap_object_class = self.converter.find_ldap_object_class(json_key)
            employee_object_class = self.converter.find_ldap_object_class("Employee")

            if ldap_object_class != employee_object_class:
                raise NotSupportedException(
                    "Mapping organization unit addresses "
                    "to non-employee objects is not supported"
                )

            affected_employees = set(
                await self.dataloader.load_mo_employees_in_org_unit(uuid)
            )
            logger.info(
                "[Listen-to-changes-in-orgs] Looping over 'n' employees.",
                n=len(affected_employees),
                **logger_args,
            )

            for affected_employee in affected_employees:
                try:
                    await self.process_employee_address(
                        affected_employee,
                        uuid,
                        changed_address,
                        json_key,
                        delete,
                        object_type,
                    )
                except DNNotFound as e:
                    logger.info("[Listen-to-changes-in-orgs] " + str(e), **logger_args)
                    continue
                except IgnoreChanges as e:
                    logger.info("[Listen-to-changes-in-orgs] " + str(e), **logger_args)
                    continue

    async def format_converted_objects(
        self,
        converted_objects,
        json_key,
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

        mo_object_class = self.converter.find_mo_object_class(json_key).split(".")[-1]

        # Load addresses already in MO
        if mo_object_class == "Address":
            if converted_objects[0].person:
                objects_in_mo = await self.dataloader.load_mo_employee_addresses(
                    converted_objects[0].person.uuid,
                    converted_objects[0].address_type.uuid,
                )
            elif converted_objects[0].org_unit:
                objects_in_mo = await self.dataloader.load_mo_org_unit_addresses(
                    converted_objects[0].org_unit.uuid,
                    converted_objects[0].address_type.uuid,
                )
            else:
                logger.info(
                    "[Format-converted-objects] Could not format converted "
                    "objects: An address needs to have either a person uuid "
                    "OR an org unit uuid"
                )
                return []
            value_key = "value"

        # Load engagements already in MO
        elif mo_object_class == "Engagement":
            objects_in_mo = await self.dataloader.load_mo_employee_engagements(
                converted_objects[0].person.uuid
            )
            value_key = "user_key"
            user_keys = [o.user_key for o in objects_in_mo]

            # If we have duplicate user_keys, remove those which are the same as the
            # primary engagement's user_key
            if len(set(user_keys)) < len(user_keys):
                primary = [
                    await self.dataloader.is_primary(o.uuid) for o in objects_in_mo
                ]

                # There can be only one primary unit. Not sure what to do if there are
                # multiple, so better just do nothing.
                if sum(primary) == 1:
                    primary_engagement = objects_in_mo[primary.index(True)]
                    logger.info(
                        "[Format-converted-objects] Found primary engagement.",
                        uuid=str(primary_engagement.uuid),
                        user_key=primary_engagement.user_key,
                    )
                    logger.info(
                        "[Format-converted-objects] Removing engagements "
                        "with identical user keys"
                    )
                    objects_in_mo = [
                        o
                        for o in objects_in_mo
                        if o == primary_engagement
                        or o.user_key != primary_engagement.user_key
                    ]

        elif mo_object_class == "ITUser":
            # If an ITUser already exists, MO throws an error - it cannot be updated if
            # the key is identical to an existing key.
            it_users_in_mo = await self.dataloader.load_mo_employee_it_users(
                converted_objects[0].person.uuid, converted_objects[0].itsystem.uuid
            )
            user_keys_in_mo = {a.user_key: a.uuid for a in it_users_in_mo}

            def mark_edit(obj) -> tuple[MOBase, Verb]:
                if obj.user_key in user_keys_in_mo:
                    obj = ITUser(
                        # Use the UUID of the existing IT user
                        uuid=user_keys_in_mo[obj.user_key],
                        # Copy all other values from the new IT user object
                        user_key=obj.user_key,
                        itsystem=obj.itsystem,
                        person=obj.person,
                        org_unit=obj.org_unit,
                        engagement=obj.engagement,
                        validity=obj.validity,
                    )
                    return obj, Verb.EDIT
                else:
                    return obj, Verb.CREATE

            return [
                mark_edit(converted_object) for converted_object in converted_objects
            ]

        else:
            return [
                (converted_object, Verb.CREATE)
                for converted_object in converted_objects
            ]

        objects_in_mo_dict = {a.uuid: a for a in objects_in_mo}
        mo_attributes = self.converter.get_mo_attributes(json_key)

        # Set uuid if a matching one is found. so an object gets updated
        # instead of duplicated
        converted_objects_uuid_checked = []
        for converted_object in converted_objects:
            values_in_mo = [getattr(a, value_key) for a in objects_in_mo_dict.values()]
            converted_object_value = getattr(converted_object, value_key)

            if values_in_mo.count(converted_object_value) == 1:
                logger.info(
                    "[Format-converted-objects] Found matching key.",
                    json_key=json_key,
                    value=getattr(converted_object, value_key),
                )

                for uuid, mo_object in objects_in_mo_dict.items():
                    value = getattr(mo_object, value_key)
                    if value == converted_object_value:
                        matching_object_uuid = uuid
                        break

                matching_object = objects_in_mo_dict[matching_object_uuid]
                converted_mo_object_dict = converted_object.dict()

                mo_object_dict_to_upload = matching_object.dict()
                for key in mo_attributes:
                    if (
                        key not in ["validity", "uuid", "objectClass"]
                        and key in converted_mo_object_dict.keys()
                    ):
                        logger.info(
                            "[Format-converted-objects] Setting "
                            f"{key} = {converted_mo_object_dict[key]}"
                        )
                        mo_object_dict_to_upload[key] = converted_mo_object_dict[key]

                mo_class = self.converter.import_mo_object_class(json_key)
                converted_object_uuid_checked = mo_class(**mo_object_dict_to_upload)

                # # If an object is identical to the one already there, it does not need
                # # to be uploaded.
                # if converted_object_uuid_checked == matching_object:
                #     logger.info(
                #         "[Format-converted-objects] Converted object is identical "
                #         "to existing object. Skipping."
                #     )
                # else:
                #     converted_objects_uuid_checked.append(converted_object_uuid_checked)
                converted_objects_uuid_checked.append(converted_object_uuid_checked)

            elif values_in_mo.count(converted_object_value) == 0:  # pragma: no cover
                converted_objects_uuid_checked.append(
                    converted_object
                )  # pragma: no cover
            else:  # pragma: no cover
                logger.warning(  # pragma: no cover
                    f"Could not determine which '{json_key}' MO object "
                    f"{value_key}='{converted_object_value}' belongs to. Skipping"
                )

            return [
                (converted_object, Verb.CREATE)
                for converted_object in converted_objects_uuid_checked
            ]

        return []  # pragma: no cover

    @wait_for_import_to_finish
    async def import_single_user(self, dn: str, force=False, manual_import=False):
        """
        Imports a single user from LDAP

        Parameters
        ----------------
        force : bool
            Can be set to 'True' to force import a user. Meaning that we do not check
            if the dn is in self.dns_to_ignore.
        """
        try:
            if not force:
                self.dns_to_ignore.check(dn)
        except IgnoreChanges as e:
            logger.info("[Import-single-user]" + str(e), dn=dn)
            return

        logger.info(
            "[Import-single-user] Importing user.",
            dn=dn,
            force=force,
            manual_import=manual_import,
        )
        detected_json_keys = self.converter.get_ldap_to_mo_json_keys()

        # Get the employee's uuid (if he exists)
        # Note: We could optimize this by loading all relevant employees once. But:
        # - What if an employee is created by someone else while this code is running?
        # - We don't need the additional speed. This is meant as a one-time import
        # - We won't gain much; This is an asynchronous request. The code moves on while
        #   we are waiting for MO's response
        employee_uuid = await self.dataloader.find_mo_employee_uuid(dn)
        if not employee_uuid:
            logger.info(
                "[Import-single-user] Employee not found in MO.",
                task="generating employee uuid",
                dn=dn,
            )
            employee_uuid = uuid4()

        # Get the employee's engagement UUID (for the engagement matching the employee's
        # AD ObjectGUID.) This depends on whether the "ADGUID" field mapping is set up
        # to map the engagement UUID into MO, so that when `import_single_user` creates
        # or updates a MO `ITUser` for "ADGUID", the relevant engagement UUID is used.
        engagement_uuid: UUID | None = await self.dataloader.find_mo_engagement_uuid(dn)
        if engagement_uuid is None:
            logger.info(
                "[Import-single-user] Engagement UUID not found in MO.",
                dn=dn,
            )
        else:
            logger.info(
                "[Import-single-user] Engagement UUID found in MO.",
                engagement_uuid=engagement_uuid,
                dn=dn,
            )

        # First import the Employee.
        # Then import the Engagement, if present in `detected_json_keys`.
        # Then finally import any other objects (Address, ITUser, etc.) which link to
        # the employee.
        priority_keys: list[str] = ["Employee"]
        if "Engagement" in detected_json_keys:
            priority_keys.append("Engagement")
        json_keys = priority_keys + [
            k for k in detected_json_keys if k not in priority_keys
        ]

        for json_key in json_keys:
            try:
                await self.perform_import_checks(dn, json_key)
            except IgnoreChanges as e:
                logger.info(f"[Import-single-user] {e}", dn=dn)
                continue

            if not self.converter._import_to_mo_(json_key, manual_import):
                logger.info(
                    "[Import-single-user] _import_to_mo_ == False.",
                    json_key=json_key,
                    dn=dn,
                )
                continue

            logger.info(
                "[Import-single-user] Loading object.", dn=dn, json_key=json_key
            )
            loaded_object = self.dataloader.load_ldap_object(
                dn,
                self.converter.get_ldap_attributes(json_key),
            )
            logger.info(
                "[Import-single-user] Loaded object.",
                dn=dn,
                json_key=json_key,
                loaded_object=loaded_object,
            )

            converted_objects = await self.converter.from_ldap(
                loaded_object,
                json_key,
                employee_uuid=employee_uuid,
                engagement_uuid=engagement_uuid,
            )

            # In case the engagement does not exist yet:
            if json_key == "Engagement" and len(converted_objects):
                engagement_uuid = converted_objects[0].uuid
                logger.info(
                    "[Import-single-user] Saving engagement UUID for DN",
                    engagement_uuid=engagement_uuid,
                    source_object=converted_objects[0],
                    dn=dn,
                )

            if len(converted_objects) == 0:
                logger.info("[Import-single-user] No converted objects", dn=dn)
                continue
            else:
                logger.info(
                    "[Import-single-user] Converted 'n' objects ",
                    n=len(converted_objects),
                    dn=dn,
                )

            try:
                converted_objects = await self.format_converted_objects(
                    converted_objects, json_key
                )
                # In case the engagement exists, but is outdated. If it exists,
                # but is identical, the list will be empty.
                if json_key == "Engagement" and len(converted_objects):
                    engagement_uuid = converted_objects[0][0].uuid
                    logger.info(
                        "[Import-single-user] Updating engagement UUID",
                        engagement_uuid=engagement_uuid,
                        source_object=converted_objects[0][0],
                        dn=dn,
                    )
            except NoObjectsReturnedException:
                # If any of the objects which this object links to does not exist
                # The dataloader will raise NoObjectsReturnedException
                #
                # This can happen, for example:
                # If converter._import_to_mo_('Address') = True
                # And converter._import_to_mo_('Employee') = False
                #
                # Because an address cannot be imported for an employee that does not
                # exist. The non-existing employee is also not created because
                # converter._import_to_mo_('Employee') = False
                logger.info(
                    "[Import-single-user] Could not format converted objects.",
                    task="Moving on",
                    dn=dn,
                )
                continue

            # TODO: Conver this to an assert? - The above try-catch ensures it is always set, no?
            if not converted_objects:  # pragma: no cover
                continue
            logger.info(
                "[Import-single-user] Importing objects.",
                converted_objects=converted_objects,
                dn=dn,
            )

            if json_key == "Custom":
                for obj, _ in converted_objects:
                    job_list = await obj.sync_to_mo(self.context)
                    for job in job_list:
                        self.uuids_to_ignore.add(job["uuid_to_ignore"])
                        await self.context["legacy_graphql_session"].execute(
                            document=job["document"],
                            variable_values=job["variable_values"],
                        )
            else:
                for mo_object, _ in converted_objects:
                    self.uuids_to_ignore.add(mo_object.uuid)
                try:
                    await self.dataloader.create_or_edit_mo_objects(converted_objects)
                except HTTPStatusError as e:
                    # This can happen, for example if a phone number in LDAP is
                    # invalid
                    logger.warning(
                        "[Import-single-user] Failed to upload objects",
                        error=e,
                        converted_objects=converted_objects,
                        request=e.request,
                        dn=dn,
                    )
                    for mo_object, _ in converted_objects:
                        self.uuids_to_ignore.remove(mo_object.uuid)

    async def refresh_object(self, uuid: UUID, object_type: str):
        """
        Sends out an AMQP message on the internal AMQP system to refresh an object
        """
        mo_object_dict = await self.dataloader.load_mo_object(str(uuid), object_type)
        routing_key = mo_object_dict["object_type"]
        payload = mo_object_dict["payload"]

        logger.info(
            "[Refresh-object] Publishing.",
            routing_key=routing_key,
            payload=payload,
        )
        await self.internal_amqpsystem.publish_message(routing_key, payload)

    async def export_org_unit_addresses_on_engagement_change(
        self, routing_key: MORoutingKey, object_uuid: UUID, **kwargs
    ):
        object_type = get_object_type_from_routing_key(routing_key)
        if object_type == "engagement":
            changed_engagement = await self.dataloader.load_mo_engagement(object_uuid)
            org_unit_uuid = changed_engagement.org_unit.uuid

            # Load UUIDs for all addresses in this org-unit
            org_unit_address_uuids = []
            for address_type_uuid in self.converter.org_unit_address_type_info.keys():
                org_unit_addresses = await self.dataloader.load_mo_org_unit_addresses(
                    org_unit_uuid,
                    address_type_uuid,
                )
                for address in org_unit_addresses:
                    org_unit_address_uuids.append(address.uuid)

            # Export this org-unit's addresses to LDAP by publishing to internal AMQP
            for org_unit_address_uuid in org_unit_address_uuids:
                await self.refresh_object(org_unit_address_uuid, "address")

    async def refresh_employee(self, employee_uuid: UUID):
        """
        Sends out AMQP-messages for all objects related to an employee
        """
        logger.info("[Refresh-employee] Refreshing employee.", uuid=str(employee_uuid))

        # Load address types and it-user types
        address_type_uuids = self.converter.employee_address_type_info.keys()
        it_system_uuids = self.converter.it_system_info.keys()

        # Load addresses
        addresses = []
        for address_type_uuid in address_type_uuids:
            addresses.extend(
                await self.dataloader.load_mo_employee_addresses(
                    employee_uuid, address_type_uuid
                )
            )

        # Load engagements
        # Note: engagement addresses are automatically picked up on engagement change
        engagements = await self.dataloader.load_mo_employee_engagements(employee_uuid)

        # Load IT-users
        it_users = []
        for it_system_uuid in it_system_uuids:
            it_users.extend(
                await self.dataloader.load_mo_employee_it_users(
                    employee_uuid, it_system_uuid
                )
            )

        # Publish messages
        for address in addresses:
            await self.refresh_object(address.uuid, "address")

        for it_user in it_users:
            await self.refresh_object(it_user.uuid, "ituser")

        for engagement in engagements:
            await self.refresh_object(engagement.uuid, "engagement")
