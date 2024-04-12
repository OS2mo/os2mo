# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""HTTP Endpoints."""
from typing import Any
from typing import Literal
from uuid import UUID
from uuid import uuid4

import structlog
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastramqpi.depends import UserContext
from fastramqpi.ramqp.depends import Context
from pydantic import ValidationError
from ramodels.mo._shared import validate_cpr
from tqdm import tqdm

from . import depends
from .dataloaders import DataLoader
from .dependencies import valid_cpr
from .exceptions import CPRFieldNotFound
from .exceptions import ObjectGUIDITSystemNotFound
from .ldap import get_attribute_types
from .ldap import paged_search
from .ldap_classes import LdapObject
from .processors import _hide_cpr as hide_cpr

logger = structlog.stdlib.get_logger()


def encode_result(result):
    # This removes all bytes objects from the result. for example images
    json_compatible_result = jsonable_encoder(
        result, custom_encoder={bytes: lambda _: None}
    )
    return json_compatible_result


def construct_router(user_context: UserContext) -> APIRouter:
    router = APIRouter()

    dataloader: DataLoader = user_context["dataloader"]
    ldap_connection = user_context["ldap_connection"]
    mapping = user_context["mapping"]

    attribute_types = get_attribute_types(ldap_connection)
    accepted_attributes = tuple(sorted(attribute_types.keys()))

    overview = dataloader.load_ldap_overview()
    ldap_classes = tuple(sorted(overview.keys()))

    default_ldap_class = mapping["mo_to_ldap"]["Employee"]["objectClass"]
    accepted_json_keys = tuple(sorted(mapping["mo_to_ldap"].keys()))

    # Load all users from LDAP, and import them into MO
    @router.get("/Import", status_code=202, tags=["Import"])
    async def import_all_objects_from_LDAP(
        sync_tool: depends.SyncTool,
        dataloader: depends.DataLoader,
        converter: depends.LdapConverter,
        test_on_first_20_entries: bool = False,
        cpr_indexed_entries_only: bool = True,
        search_base: str | None = None,
    ) -> Any:
        cpr_field = converter.cpr_field

        if cpr_indexed_entries_only and not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        all_ldap_objects = await dataloader.load_ldap_objects(
            "Employee",
            search_base=search_base,
        )

        if test_on_first_20_entries:
            # Only upload the first 20 entries
            logger.info("Slicing the first 20 entries")
            all_ldap_objects = all_ldap_objects[:20]

        number_of_entries = len(all_ldap_objects)
        logger.info("Found entries in AD", count=number_of_entries)

        with tqdm(total=number_of_entries, unit="ldap object") as progress_bar:
            progress_bar.set_description("LDAP import progress")

            # Note: This can be done in a more parallel way using asyncio.gather() but:
            # - it was experienced that fastapi throws broken pipe errors
            # - MO was observed to not handle that well either.
            # - We don't need the additional speed. This is meant as a one-time import
            for ldap_object in all_ldap_objects:
                logger.info("Importing LDAP object", dn=ldap_object.dn)
                if cpr_indexed_entries_only:
                    cpr_no = getattr(ldap_object, cpr_field)
                    try:
                        validate_cpr(cpr_no)
                    except (ValueError, TypeError):
                        logger.info("Invalid CPR Number found", dn=ldap_object.dn)
                        progress_bar.update()
                        continue

                await sync_tool.import_single_user(ldap_object.dn, manual_import=True)

                progress_bar.update()

    # Load a single user from LDAP, and import him/her/hir into MO
    @router.get("/Import/{unique_ldap_uuid}", status_code=202, tags=["Import"])
    async def import_single_user_from_LDAP(
        unique_ldap_uuid: UUID,
        sync_tool: depends.SyncTool,
        dataloader: depends.DataLoader,
    ) -> Any:
        dn = dataloader.get_ldap_dn(unique_ldap_uuid)
        await sync_tool.import_single_user(dn, manual_import=True)

    # Get all objects from LDAP - Converted to MO
    @router.get("/LDAP/{json_key}/converted", status_code=202, tags=["LDAP"])
    async def convert_all_objects_from_ldap(
        dataloader: depends.DataLoader,
        converter: depends.LdapConverter,
        json_key: Literal[accepted_json_keys],  # type: ignore
    ) -> Any:
        result = await dataloader.load_ldap_objects(json_key)
        converted_results = []
        for r in result:
            try:
                converted_results.extend(
                    await converter.from_ldap(r, json_key, employee_uuid=uuid4())
                )
            except ValidationError:
                logger.exception(
                    "Cannot convert LDAP object to MO", ldap_object=r, json_key=json_key
                )
        return converted_results

    # Get a specific cpr-indexed object from LDAP
    @router.get("/LDAP/{json_key}/{cpr}", status_code=202, tags=["LDAP"])
    async def load_object_from_LDAP(
        dataloader: depends.DataLoader,
        settings: depends.Settings,
        json_key: Literal[accepted_json_keys],  # type: ignore
        cpr: str = Depends(valid_cpr),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(
            cpr, json_key, [settings.ldap_unique_id_field]
        )
        return encode_result(result)

    # Get a specific cpr-indexed object from LDAP - Converted to MO
    @router.get("/LDAP/{json_key}/{cpr}/converted", status_code=202, tags=["LDAP"])
    async def convert_object_from_LDAP(
        dataloader: depends.DataLoader,
        converter: depends.LdapConverter,
        json_key: Literal[accepted_json_keys],  # type: ignore
        response: Response,
        cpr: str = Depends(valid_cpr),
    ) -> Any:
        result = dataloader.load_ldap_cpr_object(cpr, json_key)
        try:
            return await converter.from_ldap(result, json_key, employee_uuid=uuid4())
        except ValidationError:
            logger.exception(
                "Cannot convert LDAP object to to MO",
                ldap_object=result,
                json_key=json_key,
            )
            response.status_code = (
                status.HTTP_404_NOT_FOUND
            )  # TODO: return other status?
            return None

    # Get all objects from LDAP
    @router.get("/LDAP/{json_key}", status_code=202, tags=["LDAP"])
    async def load_all_objects_from_LDAP(
        dataloader: depends.DataLoader,
        settings: depends.Settings,
        json_key: Literal[accepted_json_keys],  # type: ignore
        entries_to_return: int = Query(ge=1),
    ) -> Any:
        result = await dataloader.load_ldap_objects(
            json_key, [settings.ldap_unique_id_field]
        )
        return encode_result(result[-entries_to_return:])

    @router.get(
        "/Inspect/non_existing_unique_ldap_uuids", status_code=202, tags=["LDAP"]
    )
    async def get_non_existing_unique_ldap_uuids_from_MO(
        settings: depends.Settings,
        dataloader: depends.DataLoader,
    ) -> Any:
        it_system_uuid = dataloader.get_ldap_it_system_uuid()
        if not it_system_uuid:
            raise ObjectGUIDITSystemNotFound("Could not find it_system_uuid")

        def to_uuid(uuid_string: str) -> UUID | str:
            try:
                return UUID(uuid_string)
            except ValueError:
                return uuid_string

        all_unique_ldap_uuids = [
            to_uuid(u)
            for u in dataloader.load_ldap_attribute_values(
                settings.ldap_unique_id_field
            )
        ]
        # TODO: Cast this to an UUID and remove the type ignore, good luck!
        all_it_users = await dataloader.load_all_current_it_users(it_system_uuid)  # type: ignore

        # Find unique ldap UUIDs which are stored in MO but do not exist in LDAP
        non_existing_unique_ldap_uuids = []
        for it_user in all_it_users:
            unique_ldap_uuid = to_uuid(it_user["user_key"])
            if unique_ldap_uuid not in all_unique_ldap_uuids:
                employee = await dataloader.load_mo_employee(it_user["employee_uuid"])
                output_dict = {
                    "name": f"{employee.givenname} {employee.surname}".strip(),
                    "MO employee uuid": employee.uuid,
                    "unique_ldap_uuid in MO": it_user["user_key"],
                }
                non_existing_unique_ldap_uuids.append(output_dict)

        return non_existing_unique_ldap_uuids

    @router.get("/Inspect/duplicate_cpr_numbers", status_code=202, tags=["LDAP"])
    async def get_duplicate_cpr_numbers_from_LDAP(
        context: Context,
        converter: depends.LdapConverter,
    ) -> Any:
        cpr_field = converter.cpr_field
        if not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        searchParameters = {
            "search_filter": "(objectclass=*)",
            "attributes": [cpr_field],
        }

        responses = [
            r
            for r in paged_search(context, searchParameters)
            if r["attributes"][cpr_field]
        ]

        cpr_values = [r["attributes"][cpr_field] for r in responses]
        output = {}

        for cpr in set(cpr_values):
            if cpr_values.count(cpr) > 1:
                output[hide_cpr(cpr)] = [
                    r["dn"] for r in responses if r["attributes"][cpr_field] == cpr
                ]

        return output

    # Get all objects from LDAP with invalid cpr numbers
    @router.get("/Inspect/invalid_cpr_numbers", status_code=202, tags=["LDAP"])
    async def get_invalid_cpr_numbers_from_LDAP(
        converter: depends.LdapConverter,
        dataloader: depends.DataLoader,
    ) -> Any:
        cpr_field = converter.cpr_field
        if not cpr_field:
            raise CPRFieldNotFound("cpr_field is not configured")

        result = await dataloader.load_ldap_objects("Employee")

        formatted_result = {}
        for entry in result:
            cpr = str(getattr(entry, cpr_field))

            try:
                validate_cpr(cpr)
            except ValueError:
                formatted_result[entry.dn] = cpr
        return formatted_result

    # Modify a person in LDAP
    @router.post("/LDAP/{json_key}", tags=["LDAP"])
    async def post_object_to_LDAP(
        dataloader: depends.DataLoader,
        json_key: Literal[accepted_json_keys],  # type: ignore
        ldap_object: LdapObject,
    ) -> Any:
        await dataloader.modify_ldap_object(ldap_object, json_key)

    # Get LDAP overview
    @router.get("/Inspect/overview", status_code=202, tags=["LDAP"])
    async def load_overview_from_LDAP(
        dataloader: depends.DataLoader,
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_overview()
        return ldap_overview[ldap_class]

    # Get LDAP overview
    @router.get("/Inspect/structure", status_code=202, tags=["LDAP"])
    async def load_structure_from_LDAP(
        dataloader: depends.DataLoader, search_base: str | None = None
    ) -> Any:
        return dataloader.load_ldap_OUs(search_base=search_base)

    # Get populated LDAP overview
    @router.get("/Inspect/overview/populated", status_code=202, tags=["LDAP"])
    async def load_populated_overview_from_LDAP(
        dataloader: depends.DataLoader,
        ldap_class: Literal[ldap_classes] = default_ldap_class,  # type: ignore
    ) -> Any:
        ldap_overview = dataloader.load_ldap_populated_overview(
            ldap_classes=[ldap_class]
        )
        return encode_result(ldap_overview.get(ldap_class))

    # Get LDAP attribute details
    @router.get("/Inspect/attribute/{attribute}", status_code=202, tags=["LDAP"])
    async def load_attribute_details_from_LDAP(
        ldap_connection: depends.Connection,
        attribute: Literal[accepted_attributes],  # type: ignore
    ) -> Any:
        attribute_types = get_attribute_types(ldap_connection)
        return attribute_types[attribute]

    # Get LDAP attribute values
    @router.get("/Inspect/attribute/values/{attribute}", status_code=202, tags=["LDAP"])
    async def load_unique_attribute_values_from_LDAP(
        dataloader: depends.DataLoader,
        attribute: Literal[accepted_attributes],  # type: ignore
        search_base: str | None = None,
    ) -> Any:
        return dataloader.load_ldap_attribute_values(attribute, search_base=search_base)

    # Get LDAP object by unique_ldap_uuid
    @router.get("/Inspect/object/unique_ldap_uuid", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap_by_unique_ldap_uuid(
        dataloader: depends.DataLoader, unique_ldap_uuid: UUID, nest: bool = False
    ) -> Any:
        dn = dataloader.get_ldap_dn(unique_ldap_uuid)
        return encode_result(dataloader.load_ldap_object(dn, ["*"], nest=nest))

    # Get LDAP object by DN
    @router.get("/Inspect/object/dn", status_code=202, tags=["LDAP"])
    async def load_object_from_ldap_by_dn(
        dataloader: depends.DataLoader, dn: str, nest: bool = False
    ) -> Any:
        return encode_result(dataloader.load_ldap_object(dn, ["*"], nest=nest))

    # Get LDAP unique_ldap_uuid
    @router.get("/unique_ldap_uuid/{dn}", status_code=202, tags=["LDAP"])
    async def load_unique_uuid_from_ldap(
        dataloader: depends.DataLoader, dn: str
    ) -> Any:
        return dataloader.get_ldap_unique_ldap_uuid(dn)

    return router
