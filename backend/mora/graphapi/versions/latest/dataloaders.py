# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Loaders for translating LoRa data to MO data to be returned from the GraphAPI."""
from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from itertools import starmap
from typing import Any
from typing import TypeVar
from uuid import UUID

from more_itertools import bucket
from more_itertools import one
from more_itertools import unique_everseen
from pydantic import parse_obj_as
from strawberry.dataloader import DataLoader

from .readers import get_role_type_by_uuid
from .readers import search_role_type
from .schema import AddressRead
from .schema import AssociationRead
from .schema import ClassRead
from .schema import EmployeeRead
from .schema import EngagementAssociationRead
from .schema import EngagementRead
from .schema import FacetRead
from .schema import ITSystemRead
from .schema import ITUserRead
from .schema import KLERead
from .schema import LeaveRead
from .schema import ManagerRead
from .schema import OrganisationRead
from .schema import OrganisationUnitRead
from .schema import OwnerRead
from .schema import RelatedUnitRead
from .schema import RoleRead
from mora.common import get_connector
from mora.service import org
from mora.util import parsedatetime
from ramodels.lora.facet import FacetRead as LFacetRead
from ramodels.lora.klasse import KlasseRead

MOModel = TypeVar(
    "MOModel",
    AddressRead,
    AssociationRead,
    ClassRead,
    EmployeeRead,
    EngagementRead,
    EngagementAssociationRead,
    FacetRead,
    ITSystemRead,
    ITUserRead,
    KLERead,
    LeaveRead,
    ManagerRead,
    OrganisationUnitRead,
    OwnerRead,
    RoleRead,
    RelatedUnitRead,
)

RoleType = TypeVar("RoleType")


def group_by_uuid(
    models: Iterable[MOModel], uuids: list[UUID] | None = None
) -> dict[UUID, list[MOModel]]:
    """Auxiliary function to group MOModels by their UUID.

    Args:
        models: List of MOModels to group.
        uuids: List of UUIDs that have been looked up. Defaults to None.

    Returns:
        A mapping of uuids and lists of corresponding MOModels.
    """
    uuids = uuids if uuids is not None else []
    buckets = bucket(models, lambda model: model.uuid)
    # unique keys in order by incoming uuid.
    # mypy doesn't like bucket for some reason
    keys = unique_everseen([*uuids, *list(buckets)])  # type: ignore
    return {key: list(buckets[key]) for key in keys}


async def get_mo(model: MOModel, **kwargs: Any) -> dict[UUID, list[MOModel]]:
    """Get data from LoRa and parse into a list of MO models.

    Args:
        model: The MO model to parse into.
        kwargs: Additional query arguments passed to LoRa.

    Returns:
        Mapping from UUID to list of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await search_role_type(mo_type, **kwargs)
    parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore
    uuid_map = group_by_uuid(parsed_results)
    return uuid_map


async def load_mo(uuids: list[UUID], model: MOModel) -> list[list[MOModel]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids: UUIDs to load.
        model: The MO model to parse into.

    Returns:
        List of parsed MO models.
    """
    mo_type = model.__fields__["type_"].default
    results = await get_role_type_by_uuid(mo_type, uuids)
    parsed_results: list[MOModel] = parse_obj_as(list[model], results)  # type: ignore
    uuid_map = group_by_uuid(parsed_results, uuids)
    return list(map(uuid_map.get, uuids))  # type: ignore


# get all models
get_org_units = partial(get_mo, model=OrganisationUnitRead)
get_employees = partial(get_mo, model=EmployeeRead)
get_engagements = partial(get_mo, model=EngagementRead)
get_engagement_associations = partial(get_mo, model=EngagementAssociationRead)
get_kles = partial(get_mo, model=KLERead)
get_addresses = partial(get_mo, model=AddressRead)
get_leaves = partial(get_mo, model=LeaveRead)
get_associations = partial(get_mo, model=AssociationRead)
get_roles = partial(get_mo, model=RoleRead)
get_itusers = partial(get_mo, model=ITUserRead)
get_managers = partial(get_mo, model=ManagerRead)
get_owners = partial(get_mo, model=OwnerRead)
get_related_units = partial(get_mo, model=RelatedUnitRead)


def lora_itsystem_to_mo_itsystem(
    lora_result: Iterable[tuple[str, dict]],
) -> Iterable[ITSystemRead]:
    def convert(systemid: str, system: dict) -> dict[str, Any]:
        attrs = system["attributter"]["itsystemegenskaber"][0]

        return {
            "uuid": systemid,
            "name": attrs.get("itsystemnavn"),
            "system_type": attrs.get("itsystemtype"),
            "user_key": attrs["brugervendtnoegle"],
        }

    objects = list(starmap(convert, lora_result))
    return parse_obj_as(list[ITSystemRead], objects)


async def get_itsystems(**kwargs: Any) -> dict[UUID, list[ITSystemRead]]:
    c = get_connector()
    lora_result = await c.itsystem.get_all(**kwargs)
    mo_models = lora_itsystem_to_mo_itsystem(lora_result)
    uuid_map = group_by_uuid(mo_models)
    return uuid_map


async def load_itsystems(uuids: list[UUID]) -> list[list[ITSystemRead]]:
    c = get_connector()
    lora_result = await c.itsystem.get_all_by_uuid(uuids)
    mo_models = lora_itsystem_to_mo_itsystem(lora_result)
    uuid_map = group_by_uuid(mo_models, uuids)
    return list(map(uuid_map.get, uuids))  # type: ignore


def lora_class_to_mo_class(lora_tuple: tuple[UUID, KlasseRead]) -> ClassRead:
    uuid, lora_class = lora_tuple

    class_attributes = one(lora_class.attributes.properties)
    class_state = one(lora_class.states.published_state)
    class_relations = lora_class.relations

    mo_class = {
        "uuid": uuid,
        "name": class_attributes.title,
        "user_key": class_attributes.user_key,
        "scope": class_attributes.scope,
        "example": class_attributes.example,
        "published": class_state.published,
        "facet_uuid": one(class_relations.facet).uuid,
        "org_uuid": one(class_relations.responsible).uuid,
        "parent_uuid": one(class_relations.parent).uuid
        if class_relations.parent
        else None,
        "owner": one(class_relations.owner).uuid if class_relations.owner else None,
    }
    return ClassRead(**mo_class)


def lora_classes_to_mo_classes(
    lora_result: Iterable[tuple[str, dict]],
) -> Iterable[ClassRead]:
    mapped_result = starmap(
        lambda uuid_str, entry: (UUID(uuid_str), parse_obj_as(KlasseRead, entry)),
        lora_result,
    )
    return map(lora_class_to_mo_class, mapped_result)


async def get_classes(**kwargs: Any) -> dict[UUID, list[ClassRead]]:
    c = get_connector()
    lora_result = await c.klasse.get_all(**kwargs)
    lora_result = format_lora_results_only_newest_relevant_lists(
        lora_result,
        relevant_lists={
            "attributter": ("klasseegenskaber",),
            "tilstande": ("klassepubliceret",),
            "relationer": ("ejer", "ansvarlig", "facet"),
        },
    )
    mo_models = lora_classes_to_mo_classes(lora_result)
    uuid_map = group_by_uuid(mo_models)
    return uuid_map


async def load_classes(uuids: list[UUID]) -> list[list[ClassRead]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids: UUIDs to load.

    Returns:
        List of parsed MO classes.
    """
    c = get_connector()
    lora_result = await c.klasse.get_all_by_uuid(uuids)
    mo_models = lora_classes_to_mo_classes(lora_result)
    uuid_map = group_by_uuid(mo_models, uuids)
    return list(map(uuid_map.get, uuids))  # type: ignore


def lora_facet_to_mo_facet(lora_tuple: tuple[UUID, LFacetRead]) -> FacetRead:
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
        "description": facet_attributes.description or "",
    }
    return FacetRead(**mo_facet)


def lora_facets_to_mo_facets(
    lora_result: Iterable[tuple[str, dict]],
) -> Iterable[FacetRead]:
    lora_facets = starmap(
        lambda uuid_str, entry: (UUID(uuid_str), parse_obj_as(LFacetRead, entry)),
        lora_result,
    )
    return map(lora_facet_to_mo_facet, lora_facets)


async def get_facets(**kwargs: Any) -> dict[UUID, list[FacetRead]]:
    c = get_connector()
    lora_result = await c.facet.get_all(**kwargs)
    mo_models = lora_facets_to_mo_facets(lora_result)
    uuid_map = group_by_uuid(mo_models)
    return uuid_map


async def load_facets(uuids: list[UUID]) -> list[list[FacetRead]]:
    """Load MO models from LoRa by UUID.

    Args:
        uuids: UUIDs to load.

    Returns:
        List of parsed MO facets.
    """
    c = get_connector()
    lora_result = await c.facet.get_all_by_uuid(uuids)
    mo_models = lora_facets_to_mo_facets(lora_result)
    uuid_map = group_by_uuid(mo_models, uuids)
    return list(map(uuid_map.get, uuids))  # type: ignore


async def load_org(keys: list[int]) -> list[OrganisationRead]:
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


async def get_loaders() -> dict[str, DataLoader | Callable]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
        "org_unit_loader": DataLoader(
            load_fn=partial(load_mo, model=OrganisationUnitRead)
        ),
        "org_unit_getter": get_org_units,
        "employee_loader": DataLoader(load_fn=partial(load_mo, model=EmployeeRead)),
        "employee_getter": get_employees,
        "engagement_loader": DataLoader(load_fn=partial(load_mo, model=EngagementRead)),
        "engagement_getter": get_engagements,
        "kle_loader": DataLoader(load_fn=partial(load_mo, model=KLERead)),
        "kle_getter": get_kles,
        "address_loader": DataLoader(load_fn=partial(load_mo, model=AddressRead)),
        "address_getter": get_addresses,
        "leave_loader": DataLoader(load_fn=partial(load_mo, model=LeaveRead)),
        "leave_getter": get_leaves,
        "association_loader": DataLoader(
            load_fn=partial(load_mo, model=AssociationRead)
        ),
        "association_getter": get_associations,
        "role_loader": DataLoader(load_fn=partial(load_mo, model=RoleRead)),
        "role_getter": get_roles,
        "ituser_loader": DataLoader(load_fn=partial(load_mo, model=ITUserRead)),
        "ituser_getter": get_itusers,
        "manager_loader": DataLoader(load_fn=partial(load_mo, model=ManagerRead)),
        "manager_getter": get_managers,
        "owner_loader": DataLoader(load_fn=partial(load_mo, model=OwnerRead)),
        "owner_getter": get_owners,
        "class_loader": DataLoader(load_fn=load_classes),
        "class_getter": get_classes,
        "rel_unit_loader": DataLoader(load_fn=partial(load_mo, model=RelatedUnitRead)),
        "rel_unit_getter": get_related_units,
        "facet_loader": DataLoader(load_fn=load_facets),
        "facet_getter": get_facets,
        "itsystem_loader": DataLoader(load_fn=load_itsystems),
        "itsystem_getter": get_itsystems,
        "engagement_association_loader": DataLoader(
            load_fn=partial(load_mo, model=EngagementAssociationRead)
        ),
        "engagement_association_getter": get_engagement_associations,
    }


def convert_lora_object_section(lora_value: list[dict]) -> list[dict]:
    """Transforms a lora_object list, to only contain the newest element.

    Ex. transform_lora_object_section(lora_object["attributter"]["klasseegenskaber"])
    """
    return [
        max(
            lora_value,
            key=lambda x: parsedatetime(x["virkning"]["from"]),
        )
    ]


def gen_paths(relevant_lists: dict[str, tuple[str, ...]]) -> Iterable[tuple[str, str]]:
    """Converts a dict representing lora-object attribute-paths to a flat list.

    Ex: `{"attributter": ("klasseegenskaber", "something",)}` becomes
    `[("attributter", "klasseegenskaber"), ("attributter", "something")...]`
    """
    for key, rel_lists in relevant_lists.items():
        for list_name in rel_lists:
            yield key, list_name


def transform_lora_object(
    relevant_paths: set[tuple[str, str]], lora_obj: dict[str, Any]
) -> None:
    """Filters LoRa object lists, based on relevant_paths, to a maximum of 1.

    Ex. {"attributter": {"klasseegenskaber": [ ELEMENT_1, ELEMENT_2 ]}} will be filtered to
    have only one element, using relevant_paths={"attributter": ("klasseegenskaber",)}

    The element choosen is the newest one, identified through the following date attr:
    ELEMENT["virkning"]["from"]
    """
    object_paths = set(gen_paths(lora_obj))
    process_paths = relevant_paths.intersection(object_paths)
    for key, list_name in process_paths:
        lora_obj[key][list_name] = convert_lora_object_section(lora_obj[key][list_name])


def format_lora_results_only_newest_relevant_lists(
    lora_results: Iterable[tuple[str, dict[str, Any]]],
    relevant_lists: dict[str, tuple[str, ...]],
) -> Iterable[tuple[str, dict]]:
    """Formats the LoRa results to only contain 1 element in list paths specified in relevant_lists.

    This method can take the result from `mora.lora.Scope.get_all()` and make sure the lora_objects
    only contain 1 element inside the lists referenced in relevant_lists.

    INFO: This was created due to the assumption that a "class/klasse" only have
    1 attribute and 1 state - but our importers break this assumption.
    """
    if not lora_results:
        return []

    relevant_paths = set(gen_paths(relevant_lists))
    for uuid, lora_obj in lora_results:
        transform_lora_object(relevant_paths, lora_obj)
        yield uuid, lora_obj
