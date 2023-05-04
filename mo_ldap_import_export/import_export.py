# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""
Created on Fri Mar  3 09:46:15 2023

@author: nick
"""
import asyncio
import datetime
from functools import wraps
from typing import Any
from typing import Callable
from typing import Union
from uuid import UUID
from uuid import uuid4

from fastramqpi.context import Context
from httpx import HTTPStatusError
from ramqp.mo.models import MORoutingKey
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType

from .exceptions import DNNotFound
from .exceptions import IgnoreChanges
from .exceptions import NoObjectsReturnedException
from .exceptions import NotSupportedException
from .ldap import cleanup
from .logging import logger


class IgnoreMe:
    def __init__(self):
        self.ignore_dict: dict[str, list[datetime.datetime]] = {}

    def __getitem__(self, key: Union[str, UUID]) -> list[datetime.datetime]:
        key = self.format_entry(key)
        if key in self.ignore_dict:
            return self.ignore_dict[key]
        else:
            return []

    def __len__(self):
        return len(self.ignore_dict)

    def format_entry(self, entry: Union[str, UUID]) -> str:
        if type(entry) is not str:
            entry = str(entry)
        return entry.lower()

    def clean(self):
        # Remove all timestamps which have been in the ignore dict for more than 60 sec.
        now = datetime.datetime.now()
        max_age = 60  # seconds
        cutoff = now - datetime.timedelta(seconds=max_age)
        for str_to_ignore, timestamps in self.ignore_dict.items():
            for timestamp in timestamps.copy():
                if timestamp < cutoff:
                    logger.info(
                        (
                            f"Removing {timestamp} belonging to {str_to_ignore} "
                            "from ignore_dict. "
                            f"It is more than {max_age} seconds old"
                        )
                    )
                    timestamps.remove(timestamp)

        # Remove keys with empty lists
        self.ignore_dict = {k: v for k, v in self.ignore_dict.items() if v}

    def add(self, str_to_add: Union[str, UUID]):
        # Add a string to the ignore dict
        str_to_add = self.format_entry(str_to_add)

        if str_to_add in self.ignore_dict:
            self.ignore_dict[str_to_add].append(datetime.datetime.now())
        else:
            self.ignore_dict[str_to_add] = [datetime.datetime.now()]

    def remove(self, str_to_remove: Union[str, UUID]):
        str_to_remove = self.format_entry(str_to_remove)

        if str_to_remove in self.ignore_dict:
            # Remove latest entry from the ignore dict
            newest_timestamp = max(self.ignore_dict[str_to_remove])
            self.ignore_dict[str_to_remove].remove(newest_timestamp)

    def check(self, str_to_check: Union[str, UUID]):
        # Raise ignoreChanges if the string to check is in self.ignore_dict
        str_to_check = self.format_entry(str_to_check)
        self.clean()

        if str_to_check in self.ignore_dict and self.ignore_dict[str_to_check]:
            # Remove timestamp so it does not get ignored twice.
            oldest_timestamp = min(self.ignore_dict[str_to_check])
            self.ignore_dict[str_to_check].remove(oldest_timestamp)
            raise IgnoreChanges(f"[check_ignore_dict] Ignoring {str_to_check}")


class SyncTool:
    def __init__(self, context: Context):

        # UUIDs in this list will be ignored by listen_to_changes ONCE
        self.uuids_to_ignore = IgnoreMe()
        self.dns_to_ignore = IgnoreMe()

        self.context = context
        self.user_context = self.context["user_context"]
        self.dataloader = self.user_context["dataloader"]
        self.converter = self.user_context["converter"]
        self.uuids_in_progress: list[UUID] = []

    @staticmethod
    def wait_for_change_to_finish(func: Callable, sleep_time: float = 2):
        """
        Runs the function normally but calls asyncio.sleep in case it is already
        running with the same uuid as input parameter
        """

        @wraps(func)
        async def modified_func(self, *args, **kwargs):
            uuid = args[0].uuid if args else kwargs["payload"].uuid

            while uuid in self.uuids_in_progress:
                logger.info(f"{uuid} in progress. Trying again in {sleep_time} seconds")
                await asyncio.sleep(sleep_time)

            self.uuids_in_progress.append(uuid)
            try:
                await func(self, *args, **kwargs)
            finally:
                self.uuids_in_progress.remove(uuid)

        return modified_func

    @wait_for_change_to_finish
    async def listen_to_changes_in_employees(
        self,
        payload: PayloadType,
        routing_key: MORoutingKey,
        delete: bool,
        current_objects_only: bool,
    ) -> None:

        logger.info("[MO] Registered change in the employee model")
        logger.info(f"[MO] uuid = {payload.uuid}")
        logger.info(f"[MO] object_uuid = {payload.object_uuid}")

        # If the object was uploaded by us, it does not need to be synchronized.
        # Note that this is not necessary in listen_to_changes_in_org_units. Because
        # those changes potentially map to multiple employees
        self.uuids_to_ignore.check(payload.object_uuid)

        try:
            dn = await self.dataloader.find_or_make_mo_employee_dn(payload.uuid)
        except DNNotFound:
            logger.info(f"DN not found for employee with uuid = {payload.uuid}")
            return

        # Get MO employee
        changed_employee = await self.dataloader.load_mo_employee(
            payload.uuid,
            current_objects_only=current_objects_only,
        )
        logger.info(f"Found Employee in MO: {changed_employee}")

        mo_object_dict: dict[str, Any] = {"mo_employee": changed_employee}

        if routing_key.object_type == ObjectType.EMPLOYEE:
            logger.info("[MO] Change registered in the employee object type")

            # Convert to LDAP
            ldap_employee = self.converter.to_ldap(mo_object_dict, "Employee", dn)

            # Upload to LDAP - overwrite because all employee fields are unique.
            # One person cannot have multiple names.
            await self.dataloader.modify_ldap_object(
                ldap_employee,
                "Employee",
                overwrite=True,
                delete=delete,
            )

        elif routing_key.object_type == ObjectType.ADDRESS:
            logger.info("[MO] Change registered in the address object type")

            # Get MO address
            changed_address = await self.dataloader.load_mo_address(
                payload.object_uuid,
                current_objects_only=current_objects_only,
            )
            address_type_uuid = str(changed_address.address_type.uuid)
            json_key = self.converter.get_employee_address_type_user_key(
                address_type_uuid
            )

            logger.info(f"Obtained address type user key = {json_key}")
            mo_object_dict["mo_employee_address"] = changed_address

            # Convert & Upload to LDAP
            await self.dataloader.modify_ldap_object(
                self.converter.to_ldap(mo_object_dict, json_key, dn),
                json_key,
                delete=delete,
            )

            addresses_in_mo = await self.dataloader.load_mo_employee_addresses(
                changed_employee.uuid, changed_address.address_type.uuid
            )

            await cleanup(
                json_key,
                "mo_employee_address",
                addresses_in_mo,
                self.user_context,
                changed_employee,
                routing_key.object_type,
                dn,
            )

        elif routing_key.object_type == ObjectType.IT:
            logger.info("[MO] Change registered in the IT object type")

            # Get MO IT-user
            changed_it_user = await self.dataloader.load_mo_it_user(
                payload.object_uuid,
                current_objects_only=current_objects_only,
            )
            it_system_type_uuid = changed_it_user.itsystem.uuid
            json_key = self.converter.get_it_system_user_key(it_system_type_uuid)

            logger.info(f"Obtained IT system name = {json_key}")
            mo_object_dict["mo_employee_it_user"] = changed_it_user

            # Convert & Upload to LDAP
            await self.dataloader.modify_ldap_object(
                self.converter.to_ldap(mo_object_dict, json_key, dn),
                json_key,
                delete=delete,
            )

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
                routing_key.object_type,
                dn,
            )

        elif routing_key.object_type == ObjectType.ENGAGEMENT:
            logger.info("[MO] Change registered in the Engagement object type")

            # Get MO Engagement
            changed_engagement = await self.dataloader.load_mo_engagement(
                payload.object_uuid,
                current_objects_only=current_objects_only,
            )

            json_key = "Engagement"
            mo_object_dict["mo_employee_engagement"] = changed_engagement

            # Convert & Upload to LDAP
            # We upload an engagement to LDAP regardless of its 'primary' attribute.
            # Because it looks like you cannot set 'primary' when creating an engagement
            # in the OS2mo GUI.
            await self.dataloader.modify_ldap_object(
                self.converter.to_ldap(mo_object_dict, json_key, dn),
                json_key,
                delete=delete,
            )

            engagements_in_mo = await self.dataloader.load_mo_employee_engagements(
                changed_employee.uuid
            )

            await cleanup(
                json_key,
                "mo_employee_engagement",
                engagements_in_mo,
                self.user_context,
                changed_employee,
                routing_key.object_type,
                dn,
            )

    @wait_for_change_to_finish
    async def process_employee_address(
        self,
        affected_employee,
        org_unit_uuid,
        changed_address,
        json_key,
        delete,
        object_type,
    ):
        dn = await self.dataloader.find_or_make_mo_employee_dn(affected_employee.uuid)

        mo_object_dict = {
            "mo_employee": affected_employee,
            "mo_org_unit_address": changed_address,
        }

        # Convert & Upload to LDAP
        await self.dataloader.modify_ldap_object(
            self.converter.to_ldap(mo_object_dict, json_key, dn),
            json_key,
            delete=delete,
        )

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
            dn,
        )

    @wait_for_change_to_finish
    async def listen_to_changes_in_org_units(
        self,
        payload: PayloadType,
        routing_key: MORoutingKey,
        delete: bool,
        current_objects_only: bool,
    ) -> None:
        logger.info("[MO] Registered change in the org_unit model")
        logger.info(f"[MO] uuid = {payload.uuid}")
        logger.info(f"[MO] object_uuid = {payload.object_uuid}")

        # When an org-unit is changed we need to update the org unit info. So we
        # know the new name of the org unit in case it was changed
        if routing_key.object_type == ObjectType.ORG_UNIT:
            logger.info("Updating org unit info")
            self.converter.org_unit_info = self.dataloader.load_mo_org_units()
            self.converter.check_org_unit_info_dict()

        if routing_key.object_type == ObjectType.ADDRESS:
            logger.info("[MO] Change registered in the address object type")

            # Get MO address
            changed_address = await self.dataloader.load_mo_address(
                payload.object_uuid,
                current_objects_only=current_objects_only,
            )
            address_type_uuid = str(changed_address.address_type.uuid)
            json_key = self.converter.get_org_unit_address_type_user_key(
                address_type_uuid
            )

            logger.info(f"Obtained address type user key = {json_key}")

            ldap_object_class = self.converter.find_ldap_object_class(json_key)
            employee_object_class = self.converter.find_ldap_object_class("Employee")

            if ldap_object_class != employee_object_class:
                raise NotSupportedException(
                    (
                        "Mapping organization unit addresses "
                        "to non-employee objects is not supported"
                    )
                )

            affected_employees = set(
                await self.dataloader.load_mo_employees_in_org_unit(payload.uuid)
            )
            logger.info(f"[MO] Found {len(affected_employees)} affected employees")

            for affected_employee in affected_employees:

                try:
                    await self.process_employee_address(
                        affected_employee,
                        payload.uuid,
                        changed_address,
                        json_key,
                        delete,
                        routing_key.object_type,
                    )
                except DNNotFound:
                    logger.info(
                        (
                            "DN not found for employee "
                            f"with uuid = {affected_employee.uuid}"
                        )
                    )
                    continue

    async def format_converted_objects(self, converted_objects, json_key):
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
                    (
                        "Could not format converted objects: "
                        "An address needs to have either a person uuid "
                        "OR an org unit uuid"
                    )
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
                        (
                            f"Found primary engagement with "
                            f"uuid={primary_engagement.uuid},"
                            f"user_key='{primary_engagement.user_key}'"
                        )
                    )
                    logger.info("Removing engagements with identical user keys")
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
            user_keys_in_mo = [a.user_key for a in it_users_in_mo]

            return [
                converted_object
                for converted_object in converted_objects
                if converted_object.user_key not in user_keys_in_mo
            ]

        else:
            return converted_objects

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
                    (
                        f"Found matching MO '{json_key}' with "
                        f"value='{getattr(converted_object,value_key)}'"
                    )
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
                        logger.info(f"Setting {key} = {converted_mo_object_dict[key]}")
                        mo_object_dict_to_upload[key] = converted_mo_object_dict[key]

                mo_class = self.converter.import_mo_object_class(json_key)
                converted_object_uuid_checked = mo_class(**mo_object_dict_to_upload)

                # If an object is identical to the one already there, it does not need
                # to be uploaded.
                if converted_object_uuid_checked == matching_object:
                    logger.info(
                        "Converted object is identical to existing object. Skipping."
                    )
                else:
                    converted_objects_uuid_checked.append(converted_object_uuid_checked)

            elif values_in_mo.count(converted_object_value) == 0:
                converted_objects_uuid_checked.append(converted_object)
            else:
                logger.warning(
                    f"Could not determine which '{json_key}' MO object "
                    f"{value_key}='{converted_object_value}' belongs to. Skipping"
                )

        return converted_objects_uuid_checked

    async def import_single_user(self, dn: str):
        """
        Imports a single user from LDAP
        """
        try:
            self.dns_to_ignore.check(dn)
        except IgnoreChanges as e:
            logger.info(e)
            return

        logger.info(f"Importing user with dn={dn}")
        detected_json_keys = self.converter.get_ldap_to_mo_json_keys()

        # Get the employee's uuid (if he exists)
        # Note: We could optimize this by loading all relevant employees once. But:
        # - What if an employee is created by someone else while this code is running?
        # - We don't need the additional speed. This is meant as a one-time import
        # - We won't gain much; This is an asynchronous request. The code moves on while
        #   we are waiting for MO's response
        employee_uuid = await self.dataloader.find_mo_employee_uuid(dn)
        if not employee_uuid:
            logger.info("Employee not found in MO - generating employee uuid")
            employee_uuid = uuid4()

        # First import the Employee
        # Then import other objects (which link to the employee)
        json_keys = ["Employee"] + [k for k in detected_json_keys if k != "Employee"]

        for json_key in json_keys:
            if not self.converter.__import_to_mo__(json_key):
                logger.info(f"__import_to_mo__ == False for json_key = '{json_key}'")
                continue
            logger.info(f"Loading {json_key} object")
            loaded_object = self.dataloader.load_ldap_object(
                dn,
                self.converter.get_ldap_attributes(json_key),
            )
            logger.info(f"Loaded {loaded_object}")

            converted_objects = self.converter.from_ldap(
                loaded_object, json_key, employee_uuid=employee_uuid
            )

            if len(converted_objects) == 0:
                logger.info("No converted objects")
                continue
            else:
                logger.info(f"Successfully converted {len(converted_objects)} objects ")

            try:
                converted_objects = await self.format_converted_objects(
                    converted_objects, json_key
                )
            except NoObjectsReturnedException:
                # If any of the objects which this object links to does not exist
                # The dataloader will raise NoObjectsReturnedException
                #
                # This can happen, for example:
                # If converter.__import_to_mo__('Address') = True
                # And converter.__import_to_mo__('Employee') = False
                #
                # Because an address cannot be imported for an employee that does not
                # exist. The non-existing employee is also not created because
                # converter.__import_to_mo__('Employee') = False
                logger.info("Could not format converted objects. Moving on.")
                continue

            if len(converted_objects) > 0:
                logger.info(f"Importing {converted_objects}")

                for mo_object in converted_objects:
                    self.uuids_to_ignore.add(mo_object.uuid)

                try:
                    await self.dataloader.upload_mo_objects(converted_objects)
                except HTTPStatusError as e:
                    # This can happen, for example if a phone number in LDAP is invalid
                    logger.warning(e)
                    for mo_object in converted_objects:
                        self.uuids_to_ignore.remove(mo_object.uuid)
