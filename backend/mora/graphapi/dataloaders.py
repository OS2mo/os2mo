#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from asyncio import gather
from functools import partial
from itertools import starmap
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar
from uuid import UUID

from more_itertools import bucket
from more_itertools import one
from pydantic import parse_obj_as
from ramodels.lora.facet import FacetRead as LFacetRead
from ramodels.lora.klasse import KlasseRead
from strawberry.dataloader import DataLoader

from mora.common import get_connector
from mora.graphapi.readers import _extract_search_params
from mora.graphapi.readers import get_role_type_by_uuid
from mora.graphapi.readers import search_role_type
from mora.graphapi.schema import AddressRead
from mora.graphapi.schema import AssociationRead
from mora.graphapi.schema import ClassRead
from mora.graphapi.schema import EmployeeRead
from mora.graphapi.schema import EngagementRead
from mora.graphapi.schema import FacetRead
from mora.graphapi.schema import ITSystemRead
from mora.graphapi.schema import ITUserRead
from mora.graphapi.schema import KLERead
from mora.graphapi.schema import LeaveRead
from mora.graphapi.schema import ManagerRead
from mora.graphapi.schema import OrganisationRead
from mora.graphapi.schema import OrganisationUnitRead
from mora.graphapi.schema import RelatedUnitRead
from mora.graphapi.schema import RoleRead
from mora.handler.reading import get_handler_for_type
from mora.service import org


# --------------------------------------------------------------------------------------
# Dataloaders
# --------------------------------------------------------------------------------------

MOModel = TypeVar(
    "MOModel",
    AddressRead,
    AssociationRead,
    EmployeeRead,
    EngagementRead,
    ITUserRead,
    KLERead,
    LeaveRead,
    ManagerRead,
    OrganisationUnitRead,
    RoleRead,
    RelatedUnitRead,
)

RoleType = TypeVar("RoleType")


async def get_mo(model: MOModel) -> List[MOModel]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        model (MOModel): The MO model to parse into.

    Returns:
        List[MOModel]: List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await search_role_type(mo_type)

    return parse_obj_as(List[model], results)  # type: ignore


async def load_mo(uuids: List[UUID], model: MOModel) -> List[Optional[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids (List[UUID]): UUIDs to load.
        model (MOModel): The MO model to parse into.

    Returns:
        List[Optional[MOModel]]: List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await get_role_type_by_uuid(mo_type, uuids)
    parsed_results = parse_obj_as(List[model], results)  # type: ignore
    uuid_map = {model.uuid: model for model in parsed_results}  # type: ignore
    return list(map(uuid_map.get, uuids))


# get all models
get_org_units = partial(get_mo, model=OrganisationUnitRead)
get_employees = partial(get_mo, model=EmployeeRead)
get_engagements = partial(get_mo, model=EngagementRead)
get_kles = partial(get_mo, model=KLERead)
get_addresses = partial(get_mo, model=AddressRead)
get_leaves = partial(get_mo, model=LeaveRead)
get_associations = partial(get_mo, model=AssociationRead)
get_roles = partial(get_mo, model=RoleRead)
get_itusers = partial(get_mo, model=ITUserRead)
get_managers = partial(get_mo, model=ManagerRead)
get_related_units = partial(get_mo, model=RelatedUnitRead)


def lora_itsystem_to_mo_itsystem(
    lora_result: Iterable[Tuple[str, dict]],
) -> Iterable[ITSystemRead]:
    def convert(systemid: str, system: dict) -> Dict[str, Any]:
        attrs = system["attributter"]["itsystemegenskaber"][0]

        return {
            "uuid": systemid,
            "name": attrs.get("itsystemnavn"),
            "system_type": attrs.get("itsystemtype"),
            "user_key": attrs["brugervendtnoegle"],
        }

    objects = list(starmap(convert, lora_result))
    return parse_obj_as(List[ITSystemRead], objects)


async def get_itsystems() -> List[ITSystemRead]:
    c = get_connector()
    lora_result = await c.itsystem.get_all()
    mo_models = lora_itsystem_to_mo_itsystem(lora_result)
    return list(mo_models)


async def load_itsystems(uuids: List[UUID]) -> List[Optional[ITSystemRead]]:
    c = get_connector()
    lora_result = await c.itsystem.get_all_by_uuid(uuids)
    mo_models = lora_itsystem_to_mo_itsystem(lora_result)
    uuid_map = {model.uuid: model for model in mo_models}  # type: ignore
    return list(map(uuid_map.get, uuids))


def lora_class_to_mo_class(lora_tuple: Tuple[UUID, KlasseRead]) -> ClassRead:
    uuid, lora_class = lora_tuple

    class_attributes = one(lora_class.attributes.properties)
    class_state = one(lora_class.states.published_state)
    class_relations = lora_class.relations

    mo_class = {
        "uuid": uuid,
        "name": class_attributes.title,
        "user_key": class_attributes.user_key,
        "scope": class_attributes.scope,
        "published": class_state.published,
        "facet_uuid": one(class_relations.facet).uuid,
        "org_uuid": one(class_relations.responsible).uuid,
        "parent_uuid": class_relations.parent.uuid if class_relations.parent else None,
    }
    return ClassRead(**mo_class)


def lora_classes_to_mo_classes(
    lora_result: Iterable[Tuple[str, dict]],
) -> Iterable[ClassRead]:
    mapped_result = map(lambda entry: (entry[0], KlasseRead(**entry[1])), lora_result)
    return map(lora_class_to_mo_class, mapped_result)  # type: ignore


async def get_classes() -> List[ClassRead]:
    c = get_connector()
    lora_result = await c.klasse.get_all()
    mo_models = lora_classes_to_mo_classes(lora_result)
    return list(mo_models)


async def load_classes(uuids: List[UUID]) -> List[Optional[ClassRead]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids (List[UUID]): UUIDs to load.

    Returns:
        List[Optional[ClassRead]]: List of parsed MO classes.
    """
    c = get_connector()
    lora_result = await c.klasse.get_all_by_uuid(uuids)
    mo_models = lora_classes_to_mo_classes(lora_result)
    uuid_map = {model.uuid: model for model in mo_models}  # type: ignore
    return list(map(uuid_map.get, uuids))


async def load_class_children(parent_uuids: List[UUID]) -> List[ClassRead]:
    c = get_connector()
    lora_result = await c.klasse.get_all(overordnetklasse=list(map(str, parent_uuids)))
    mo_models = lora_classes_to_mo_classes(lora_result)
    buckets = bucket(mo_models, key=lambda model: model.parent_uuid)
    return list(map(lambda key: buckets[key], parent_uuids))


def lora_facet_to_mo_facet(lora_tuple: Tuple[UUID, LFacetRead]) -> FacetRead:
    uuid, lora_facet = lora_tuple

    facet_attributes = one(lora_facet.attributes.properties)
    facet_state = one(lora_facet.states.published_state)
    facet_relations = lora_facet.relations

    mo_facet = {
        "uuid": uuid,
        "user_key": facet_attributes.user_key,
        "published": facet_state.published,
        "org_uuid": one(facet_relations.responsible).uuid,
        "parent_uuid": (
            one(facet_relations.parent).uuid
            if facet_relations.parent is not None
            else None
        ),
    }
    return FacetRead(**mo_facet)


def lora_facets_to_mo_facets(
    lora_result: Iterable[Tuple[str, dict]],
) -> Iterable[FacetRead]:
    lora_result = map(lambda entry: (entry[0], LFacetRead(**entry[1])), lora_result)
    return map(lora_facet_to_mo_facet, lora_result)  # type: ignore


async def get_facets() -> List[FacetRead]:
    c = get_connector()
    lora_result = await c.facet.get_all()
    mo_models = lora_facets_to_mo_facets(lora_result)
    return list(mo_models)


async def load_facets(uuids: List[UUID]) -> List[Optional[FacetRead]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids (List[UUID]): UUIDs to load.

    Returns:
        List[Optional[FacetRead]]: List of parsed MO facets.
    """
    c = get_connector()
    lora_result = await c.facet.get_all_by_uuid(uuids)
    mo_models = lora_facets_to_mo_facets(lora_result)
    uuid_map = {model.uuid: model for model in mo_models}  # type: ignore
    return list(map(uuid_map.get, uuids))


async def load_facet_classes(facet_uuids: List[UUID]) -> List[ClassRead]:
    c = get_connector()
    lora_result = await c.klasse.get_all(facet=list(map(str, facet_uuids)))
    mo_models = lora_classes_to_mo_classes(lora_result)
    buckets = bucket(mo_models, key=lambda model: model.facet_uuid)
    return list(map(lambda key: buckets[key], facet_uuids))


async def get_employee_details(
    employee_uuid: UUID, role_type: str
) -> Optional[List[MOModel]]:
    """Non-bulk loader for employee details."""
    c = get_connector()
    cls = get_handler_for_type(role_type)
    result = await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={
                "at": None,
                "validity": None,
                "tilknyttedebrugere": str(employee_uuid),
            }
        ),
        changed_since=None,
    )
    return parse_obj_as(List[MOModel], result)


async def load_employee_details(
    keys: List[UUID], model: MOModel
) -> List[List[MOModel]]:
    """Non-bulk loader for employee details with bulk interface."""
    mo_type = model.__fields__["type_"].default
    tasks = map(partial(get_employee_details, role_type=mo_type), keys)
    return await gather(*tasks)


async def get_org_unit_details(
    org_unit_uuid: UUID, role_type: str
) -> Optional[List[MOModel]]:
    """Non-bulk loader for organisation unit details."""
    c = get_connector()
    cls = get_handler_for_type(role_type)
    result = await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={
                "at": None,
                "validity": None,
                "tilknyttedeenheder": str(org_unit_uuid),
            }
        ),
        changed_since=None,
    )
    return parse_obj_as(List[MOModel], result)


async def load_org_unit_details(
    keys: List[UUID], model: MOModel
) -> List[List[MOModel]]:
    """Non-bulk loader for org_unit details with bulk interface."""
    mo_type = model.__fields__["type_"].default
    tasks = map(partial(get_org_unit_details, role_type=mo_type), keys)
    return await gather(*tasks)


async def load_org(keys: List[int]) -> List[OrganisationRead]:
    """Dataloader function to load Organisation.

    A dataloader is used even though only a single Organisation can ever exist, as the
    dataloader also implements caching, which is useful as there may be more than
    one reference to the organisation within one query.
    """
    # We fake the ID of our Organisation as 0 and expect nothing else as inputs
    keyset = set(keys)
    if keyset != {0}:
        raise ValueError("Only one organisation can exist!")

    obj = await org.get_configured_organisation()
    return [OrganisationRead.parse_obj(obj)] * len(keys)


async def get_org_unit_children(parent_uuid: UUID) -> List[MOModel]:
    """Non-bulk loader for organisation unit children."""
    c = get_connector()
    cls = get_handler_for_type(OrganisationUnitRead.__fields__["type_"].default)
    result = await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={
                "at": None,
                "validity": None,
                "overordnet": str(parent_uuid),
                "gyldighed": "Aktiv",
            }
        ),
        changed_since=None,
    )
    return parse_obj_as(List[MOModel], result)


async def load_org_units_children(keys: List[UUID]) -> List[List[MOModel]]:
    """Non-bulk loader for organisation unit children with bulk interface."""
    # TODO: This function should be replaced with a bulk version
    tasks = map(get_org_unit_children, keys)
    return await gather(*tasks)


async def get_loaders() -> Dict[str, DataLoader]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        "org_unit_loader": DataLoader(
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "org_unit_children_loader": DataLoader(load_fn=load_org_units_children),
        "org_unit_manager_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=ManagerRead)
        ),
        "org_unit_address_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=AddressRead)
        ),
        "org_unit_engagement_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=EngagementRead)
        ),
        "org_unit_leave_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=LeaveRead)
        ),
        "org_unit_association_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=AssociationRead)
        ),
        "org_unit_role_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=RoleRead)
        ),
        "org_unit_ituser_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=ITUserRead)
        ),
        "org_unit_kle_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=KLERead)
        ),
        "org_unit_related_unit_loader": DataLoader(
            load_fn=partial(load_org_unit_details, model=RelatedUnitRead)
        ),
        "employee_loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
        "employee_manager_role_loader": DataLoader(
            load_fn=partial(load_employee_details, model=ManagerRead)
        ),
        "employee_address_loader": DataLoader(
            load_fn=partial(load_employee_details, model=AddressRead)
        ),
        "employee_engagement_loader": DataLoader(
            load_fn=partial(load_employee_details, model=EngagementRead)
        ),
        "employee_leave_loader": DataLoader(
            load_fn=partial(load_employee_details, model=LeaveRead)
        ),
        "employee_association_loader": DataLoader(
            load_fn=partial(load_employee_details, model=AssociationRead)
        ),
        "employee_role_loader": DataLoader(
            load_fn=partial(load_employee_details, model=RoleRead)
        ),
        "employee_ituser_loader": DataLoader(
            load_fn=partial(load_employee_details, model=ITUserRead)
        ),
        "engagement_loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
        "kle_loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
        "address_loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
        "leave_loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
        "association_loader": DataLoader(
            load_fn=partial(load_mo, model=AssociationRead)
        ),
        "role_loader": DataLoader(load_fn=partial(load_mo, model=RoleRead)),
        "ituser_loader": DataLoader(load_fn=partial(load_mo, model=ITUserRead)),
        "manager_loader": DataLoader(load_fn=partial(load_mo, model=ManagerRead)),
        "class_loader": DataLoader(load_fn=load_classes),
        "rel_unit_loader": DataLoader(load_fn=partial(load_mo, model=RelatedUnitRead)),
        "class_children_loader": DataLoader(load_fn=load_class_children),
        "facet_loader": DataLoader(load_fn=load_facets),
        "facet_classes_loader": DataLoader(load_fn=load_facet_classes),
        "itsystem_loader": DataLoader(load_fn=load_itsystems),
    }
