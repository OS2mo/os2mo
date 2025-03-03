# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Organisational units
--------------------

This section describes how to interact with organisational units.

For more information regarding reading relations involving organisational
units, refer to http:get:`/service/(any:type)/(uuid:id)/details/`

"""

import copy
import enum
import locale
import logging
from datetime import date
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Query
from more_itertools import flatten
from more_itertools import last
from more_itertools import unzip

from mora.auth.keycloak import oidc
from mora.request_scoped.bulking import get_lora_object
from mora.service.util import get_configuration

from .. import common
from .. import config
from .. import depends
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..graphapi.middleware import is_graphql
from ..handler.reading import get_handler_for_type
from ..lora import LoraObjectType
from ..triggers import Trigger
from . import autocomplete
from . import facet
from . import handlers
from . import org
from .tree_helper import prepare_ancestor_tree
from .validation import validator

router = APIRouter()

logger = logging.getLogger(__name__)


@enum.unique
class UnitDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with child count
    NCHILDREN = 1

    # with everything except child count
    SELF = 2

    # same as above, but with all parents
    FULL = 3

    # name, path and UUID
    PATH = 5


class OrgUnitRequestHandler(handlers.RequestHandler):
    role_type = "org_unit"

    async def prepare_create(self, req):
        name = util.checked_get(req, mapping.NAME, "", required=True)

        unitid = util.get_uuid(req, required=False) or str(uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, unitid)

        org_uuid = (await org.get_configured_organisation())["uuid"]

        parent_uuid = util.get_mapping_uuid(req, mapping.PARENT)
        if parent_uuid is None:
            parent_uuid = org_uuid

        org_unit_type_uuid = util.get_mapping_uuid(
            req, mapping.ORG_UNIT_TYPE, required=False
        )

        time_planning_uuid = util.get_mapping_uuid(
            req, mapping.TIME_PLANNING, required=False
        )

        org_unit_level = util.get_mapping_uuid(
            req, mapping.ORG_UNIT_LEVEL, required=False
        )

        org_unit_hierarchy = util.get_mapping_uuid(
            req, mapping.ORG_UNIT_HIERARCHY, required=False
        )

        valid_from = util.get_valid_from(req)
        valid_to = util.get_valid_to(req)

        org_unit = common.create_organisationsenhed_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            enhedsnavn=name,
            brugervendtnoegle=bvn,
            tilhoerer=org_uuid,
            enhedstype=org_unit_type_uuid,
            opgaver=[
                {
                    "objekttype": "tidsregistrering",
                    "uuid": time_planning_uuid,
                },
            ]
            if time_planning_uuid
            else [],
            niveau=org_unit_level,
            opmærkning=org_unit_hierarchy,
            overordnet=parent_uuid,
        )

        if org_uuid != parent_uuid:
            await validator.is_date_range_in_org_unit_range(
                {"uuid": parent_uuid}, valid_from, valid_to
            )

        def _inject_org_units(details, org_unit_uuid, valid_from, valid_to):
            decorated = copy.deepcopy(details)
            for detail in decorated:
                detail["org_unit"] = {
                    mapping.UUID: org_unit_uuid,
                    mapping.VALID_FROM: valid_from,
                    mapping.VALID_TO: valid_to,
                    "allow_nonexistent": True,
                }

            return decorated

        details = util.checked_get(req, "details", [])
        details_with_org_units = _inject_org_units(
            details, unitid, valid_from, valid_to
        )

        self.details_requests = await handlers.generate_requests(
            details_with_org_units, mapping.RequestType.CREATE
        )

        self.payload = org_unit
        self.uuid = unitid
        self.trigger_dict[Trigger.ORG_UNIT_UUID] = unitid

    async def prepare_edit(self, req: dict):
        original_data = util.checked_get(req, "original", {}, required=False)
        data = util.checked_get(req, "data", {}, required=True)

        unitid = util.get_uuid(data, fallback=original_data)

        # Get the current org-unit which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationenhed.get(uuid=unitid)

        if not original:  # pragma: no cover
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=unitid)

        new_from, new_to = util.get_validities(data)

        clamp = util.checked_get(data, "clamp", False)

        if clamp:
            new_to = min(
                new_to,
                max(
                    util.get_effect_to(effect)
                    for effect in mapping.ORG_UNIT_GYLDIGHED_FIELD.get(original)
                    if effect["gyldighed"] == "Aktiv"
                ),
            )

        # Get org unit uuid for validation purposes
        payload = {"note": "Rediger organisationsenhed"}

        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "organisationenhedgyldighed"),
            )

            original_uuid = util.get_mapping_uuid(original_data, mapping.ORG_UNIT)

            if original_uuid and original_uuid != unitid:  # pragma: no cover
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    "cannot change unit uuid!",
                )

        update_fields = []

        # Always update gyldighed
        update_fields.append((mapping.ORG_UNIT_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

        def get_lora_dict_current_attr(
            lora_dict: dict, from_date: datetime, to_date: datetime
        ):
            """Returns the current active attribute for a LoRa dict/obj.

            LoRa-Connector-Scopes returns objects with atrributes, and others, which are
            unordered lists. The old logic assumed the last element was the current element,
            which we still implement through last(), but now also filter the attributes based
            on its date related to the given "from_date" and "to_date".
            """

            return last(
                filter(
                    lambda a: (
                        util.get_effect_from(a) <= to_date
                        and util.get_effect_to(a) > from_date
                    ),
                    mapping.ORG_UNIT_EGENSKABER_FIELD(lora_dict),
                ),
                default={},
            ).copy()

        try:
            attributes = get_lora_dict_current_attr(original, new_from, new_to)
        except (TypeError, LookupError):  # pragma: no cover
            attributes = {}

        changed_props = {}

        if mapping.USER_KEY in data:
            changed_props["brugervendtnoegle"] = data[mapping.USER_KEY]

        if mapping.NAME in data:
            changed_props["enhedsnavn"] = data[mapping.NAME]

        if attributes or changed_props:
            update_fields.append(
                (
                    mapping.ORG_UNIT_EGENSKABER_FIELD,
                    {
                        **attributes,
                        **changed_props,
                    },
                )
            )

        if mapping.ORG_UNIT_TYPE in data:
            update_fields.append(
                (
                    mapping.ORG_UNIT_TYPE_FIELD,
                    {"uuid": data[mapping.ORG_UNIT_TYPE]["uuid"]},
                )
            )

        if data.get(mapping.ORG_UNIT_LEVEL):
            org_unit_level = util.get_mapping_uuid(data, mapping.ORG_UNIT_LEVEL)
            update_fields.append(
                (mapping.ORG_UNIT_LEVEL_FIELD, {"uuid": org_unit_level})
            )

        if data.get(mapping.ORG_UNIT_HIERARCHY):  # pragma: no cover
            org_unit_hierarchy = util.get_mapping_uuid(data, mapping.ORG_UNIT_HIERARCHY)
            update_fields.append(
                (mapping.ORG_UNIT_HIERARCHY_FIELD, {"uuid": org_unit_hierarchy})
            )

        if mapping.TIME_PLANNING in data and data.get(mapping.TIME_PLANNING):
            update_fields.append(
                (
                    mapping.ORG_UNIT_TIME_PLANNING_FIELD,
                    {
                        "objekttype": "tidsregistrering",
                        "uuid": data[mapping.TIME_PLANNING]["uuid"],
                    },
                )
            )

        if mapping.PARENT in data:
            parent_uuid = util.get_mapping_uuid(data, mapping.PARENT)
            # Default to root org unit if this unit has no parent
            if parent_uuid is None:
                parent_uuid = (await org.get_configured_organisation())["uuid"]
            else:
                await validator.is_date_range_in_org_unit_range(
                    {"uuid": parent_uuid}, new_from, new_to
                )
            # Validate consequences of changing the parent
            await validator.is_candidate_parent_valid(unitid, parent_uuid, new_from)

            update_fields.append((mapping.PARENT_FIELD, {"uuid": parent_uuid}))

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ORG_UNIT_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.payload = payload
        self.uuid = unitid
        self.trigger_dict[Trigger.ORG_UNIT_UUID] = unitid

    async def prepare_terminate(self, request: dict):
        virkning = OrgUnitRequestHandler.get_virkning_for_terminate(request)

        obj_path = ("tilstande", "organisationenhedgyldighed")
        val_inactive = {
            "gyldighed": "Inaktiv",
            "virkning": virkning,
        }

        payload = util.set_obj_value({}, obj_path, [val_inactive])
        payload["note"] = "Afslut enhed"

        self.payload = payload
        self.uuid = util.get_uuid(request)
        self.trigger_dict[Trigger.ORG_UNIT_UUID] = self.uuid

    async def prepare_refresh(self, request: dict):
        unitid = request[mapping.UUID]
        self.uuid = unitid
        self.trigger_dict[Trigger.ORG_UNIT_UUID] = unitid

    async def submit(self) -> str:
        c = lora.Connector()

        if self.request_type == mapping.RequestType.CREATE:
            self.result = await c.organisationenhed.create(self.payload, self.uuid)
            # coverage: pause
            if self.details_requests:
                for r in self.details_requests:
                    await r.submit()
            # coverage: unpause

        elif self.request_type == mapping.RequestType.REFRESH:
            pass
        else:
            self.result = await c.organisationenhed.update(self.payload, self.uuid)

        submit = await super().submit()
        if self.request_type == mapping.RequestType.REFRESH:
            return {
                "message": "\n".join(
                    map(str, self.trigger_results_before + self.trigger_results_after)
                )
            }
        # coverage: pause
        return submit
        # coverage: unpause


async def request_bulked_get_one_orgunit(
    unitid: str,
    details: UnitDetails = UnitDetails.NCHILDREN,
    validity: Any | None = None,
    only_primary_uuid: bool = False,
):
    connector = common.get_connector()
    return await get_one_orgunit(
        c=connector,
        unitid=unitid,
        unit=await get_lora_object(
            type_=LoraObjectType.org_unit, uuid=unitid, connector=connector
        )
        if not only_primary_uuid
        else None,
        details=details,
        validity=validity,
        only_primary_uuid=only_primary_uuid,
    )


async def get_one_orgunit(
    c: lora.Connector,
    unitid,
    unit=None,
    details=UnitDetails.NCHILDREN,
    validity=None,
    only_primary_uuid: bool = False,
    count_related: dict = None,
) -> dict[Any, Any] | None:
    """
    Internal API for returning one organisation unit.
    """
    if only_primary_uuid:
        return {mapping.UUID: unitid}

    if not unit:  # optional early exit
        unit = await get_lora_object(LoraObjectType.org_unit, uuid=unitid)

        if not unit or not util.is_reg_valid(unit):
            return None
    attrs = unit["attributter"]["organisationenhedegenskaber"][0]
    rels = unit["relationer"]
    validities = unit["tilstande"]["organisationenhedgyldighed"]

    unittype = mapping.ORG_UNIT_TYPE_FIELD.get_uuid(unit)
    timeplanning = mapping.ORG_UNIT_TIME_PLANNING_FIELD.get_uuid(unit)
    org_unit_level = mapping.ORG_UNIT_LEVEL_FIELD.get_uuid(unit)
    org_unit_hierarchy = mapping.ORG_UNIT_HIERARCHY_FIELD.get_uuid(unit)
    parentid = rels["overordnet"][0]["uuid"]
    r = {
        "name": attrs["enhedsnavn"],
        "user_key": attrs["brugervendtnoegle"],
        "uuid": unitid,
    }
    if is_graphql():
        org_unit_hierarchy = mapping.ORG_UNIT_HIERARCHY_FIELD.get_uuid(unit)
        r.update(
            {
                "unit_type_uuid": unittype,
                "time_planning_uuid": timeplanning,
                "org_unit_level_uuid": org_unit_level,
                "parent_uuid": parentid,
                "org_unit_hierarchy": org_unit_hierarchy,
            }
        )

    if details is UnitDetails.NCHILDREN:
        children = await c.organisationenhed.load_uuids(
            overordnet=unitid,
            gyldighed="Aktiv",
        )
        r["child_count"] = len(children)
    elif details is UnitDetails.FULL or details is UnitDetails.PATH:
        parent = await request_bulked_get_one_orgunit(
            unitid=parentid, details=details, only_primary_uuid=only_primary_uuid
        )

        if details is UnitDetails.FULL:
            r[mapping.PARENT] = parent
            r[mapping.ORG] = await org.get_configured_organisation()

            r[mapping.ORG_UNIT_TYPE] = (
                await facet.request_bulked_get_one_class_full(
                    classid=unittype, only_primary_uuid=only_primary_uuid
                )
                if unittype
                else None
            )

            r[mapping.TIME_PLANNING] = (
                await facet.request_bulked_get_one_class_full(
                    classid=timeplanning, only_primary_uuid=only_primary_uuid
                )
                if timeplanning
                else None
            )

            r[mapping.ORG_UNIT_LEVEL] = (
                await facet.request_bulked_get_one_class_full(
                    classid=org_unit_level, only_primary_uuid=only_primary_uuid
                )
                if org_unit_level
                else None
            )

            r[mapping.ORG_UNIT_HIERARCHY] = (
                await facet.request_bulked_get_one_class_full(
                    classid=org_unit_hierarchy, only_primary_uuid=only_primary_uuid
                )
                if org_unit_hierarchy
                else None
            )

        if parentid is not None:
            if parent and parent[mapping.LOCATION]:
                r[mapping.LOCATION] = (
                    parent[mapping.LOCATION] + "\\" + parent[mapping.NAME]
                )
            elif parent:
                r[mapping.LOCATION] = parent[mapping.NAME]
            else:
                r[mapping.LOCATION] = ""

            if details is UnitDetails.FULL:
                settings = {}
                local_settings = {}

                settings.update(local_settings)
                if parent:
                    parent_settings = parent[mapping.USER_SETTINGS]["orgunit"]
                    for setting, value in parent_settings.items():
                        settings.setdefault(setting, value)

                global_settings = await get_configuration()
                for setting, value in global_settings.items():
                    settings.setdefault(setting, value)

                r[mapping.USER_SETTINGS] = {"orgunit": settings}

    elif details is UnitDetails.SELF:  # pragma: no cover
        r[mapping.ORG] = await org.get_configured_organisation()

        r[mapping.PARENT] = await request_bulked_get_one_orgunit(
            unitid=parentid,
            details=UnitDetails.MINIMAL,
            only_primary_uuid=only_primary_uuid,
        )

        r[mapping.ORG] = await org.get_configured_organisation()

        r[mapping.ORG_UNIT_TYPE] = (
            await facet.request_bulked_get_one_class_full(
                classid=unittype, only_primary_uuid=only_primary_uuid
            )
            if unittype
            else None
        )

        r[mapping.TIME_PLANNING] = (
            await facet.request_bulked_get_one_class_full(
                classid=timeplanning, only_primary_uuid=only_primary_uuid
            )
            if timeplanning
            else None
        )

        r[mapping.ORG_UNIT_LEVEL] = (
            await facet.request_bulked_get_one_class_full(
                classid=org_unit_level, only_primary_uuid=only_primary_uuid
            )
            if org_unit_level
            else None
        )

        r[mapping.ORG_UNIT_HIERARCHY] = (
            await facet.request_bulked_get_one_class_full(
                classid=org_unit_hierarchy, only_primary_uuid=only_primary_uuid
            )
            if org_unit_hierarchy
            else None
        )

    elif details is UnitDetails.MINIMAL:
        pass  # already done
    else:  # pragma: no cover
        raise AssertionError(f"enum is {details}!?")

    r[mapping.VALIDITY] = validity or util.get_effect_validity(validities[0])

    count_related = count_related or {}
    for key, reader in count_related.items():
        r["%s_count" % key] = await reader.get_count(c, "ou", unitid)

    return r


@router.get("/ou/autocomplete/")
async def autocomplete_orgunits(
    session: depends.Session,
    query: str,
    at: date | None = Query(
        None,
        description='The "at date" to use, e.g. `2020-01-31`. '
        "Results are only included if they are active at the specified date.",
    ),
):
    settings = config.get_settings()

    # Use LEGACY
    if settings.confdb_autocomplete_v2_use_legacy:
        logger.debug("using autocomplete_orgunits_v2 legacy")
        return await autocomplete.get_results(
            "organisationsenhed", settings.confdb_autocomplete_attrs_orgunit, query
        )

    logger.debug("using autocomplete_orgunits_v2 new")
    search_results = await autocomplete.search_orgunits(session, query, at)

    # Decorate search results with data through GraphQL
    return {
        "items": await autocomplete.decorate_orgunit_search_result(
            settings, search_results, at
        )
    }


@router.get("/ou/ancestor-tree")
async def get_unit_ancestor_tree(
    uuid: list[UUID] = Query(...),
    only_primary_uuid: bool = Query(False),
    org_unit_hierarchy: str = "",
):
    """Obtain the tree of ancestors for the given units.

    The tree includes siblings of ancestors, with their child counts:

    * Every ancestor of each unit.
    * Every sibling of every ancestor, with a child count.

    The intent of this routine is to enable easily showing the tree
    *up to and including* the given units in the UI.

    .. :quickref: Unit; Ancestor tree

    :query unitid: the UUID of the organisational unit. *Required*.
    :query at: the 'at date' to use, e.g. '2020-01-28'. *Optional*.
               The tree returned will only include organisational units that
               were valid at the specified 'at date'.
    :query count: the name(s) of related objects to count for each unit.
                  *Optional*. If `count=association`, each organisational unit
                  in the tree is annotated with an additional
                  `association_count` key which contains the number of
                  associations in the unit. `count=engagement` is also allowed.
                  It is allowed to pass more than one `count` query parameter.
    :query org_unit_hierarchy: the UUID of an optional 'org unit hierarchy'.
                               *Optional*. The tree returned is filtered to
                               contain only organisational units which belong
                               to the given hierarchy.

    :see: :http:get:`/service/ou/(uuid:unitid)/`

    **Example Response**:

    .. sourcecode:: json

     [{
        "children": [
          {
            "child_count": 2,
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {
              "from": "2016-01-01",
              "to": null
            }
          },
          {
            "child_count": 0,
            "name": "Samfundsvidenskabelige fakultet",
            "user_key": "samf",
            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {
              "from": "2017-01-01",
              "to": null
            }
          }
        ],
        "name": "Overordnet Enhed",
        "user_key": "root",
        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
        "validity": {
          "from": "2016-01-01",
          "to": null
        }
      }]

    """

    allowed = {"association", "engagement"}
    given = set(util.get_query_args().getlist("count"))
    invalid = given - allowed
    if invalid:  # pragma: no cover
        exceptions.ErrorCodes.E_INVALID_INPUT(
            'invalid value(s) for "count" query parameter: %r' % invalid
        )

    c = common.get_connector()
    count_related = {t: get_handler_for_type(t) for t in given}

    unitids = list(map(str, uuid))
    return await get_unit_tree(
        c,
        unitids,
        with_siblings=True,
        only_primary_uuid=only_primary_uuid,
        org_unit_hierarchy=org_unit_hierarchy,
        count_related=count_related,
    )


async def get_unit_tree(
    c: lora.Connector,
    unitids: list[str],
    with_siblings: bool = False,
    only_primary_uuid: bool = False,
    org_unit_hierarchy: str = None,
    count_related: dict | None = None,
):
    """Return a tree, bounded by the given unitid.

    The tree includes siblings of ancestors, with their child counts.
    """

    async def get_unit(unitid):
        details = (
            UnitDetails.NCHILDREN
            if with_siblings and unitid not in children
            else UnitDetails.MINIMAL
        )
        r = await get_one_orgunit(
            c,
            unitid,
            cache[unitid],
            details=details,
            only_primary_uuid=only_primary_uuid,
            count_related=count_related,
        )
        if unitid in children:
            r["children"] = await get_units(children[unitid])
        return r

    async def get_units(unitids):
        units = [await get_unit(uid) for uid in unitids]
        return sorted(units, key=lambda u: locale.strxfrm(u[mapping.NAME]))

    def get_children_args(uuid, parent_uuid, cache):
        def get_org(uuid, cache):
            for orgid in mapping.BELONGS_TO_FIELD.get_uuids(cache[uuid]):
                return orgid

        args = {
            "overordnet": parent_uuid,
            "tilhoerer": get_org(uuid, cache),
            "gyldighed": "Aktiv",
        }

        if org_unit_hierarchy:  # pragma: no cover
            args.update({mapping.ORG_UNIT_HIERARCHY_KEY: org_unit_hierarchy})

        return args

    root_uuids, children, cache = await prepare_ancestor_tree(
        c.organisationenhed,
        mapping.PARENT_FIELD,
        unitids,
        get_children_args,
        with_siblings=with_siblings,
    )
    # Strip off one level
    root_uuids = set(flatten([children[uuid] for uuid in root_uuids]))

    return await get_units(root for root in root_uuids)


@router.get("/ou/{unitid}/refresh")
async def trigger_external_integration(unitid: UUID, only_primary_uuid: bool = False):
    """
    Trigger external integration for a given org unit UUID
    :param unitid: The UUID of the org unit to trigger for
    """
    unitid = str(unitid)

    c = common.get_connector()

    org_unit = await get_one_orgunit(
        c, unitid, details=UnitDetails.FULL, only_primary_uuid=only_primary_uuid
    )
    if not org_unit:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=unitid)

    request = {}
    request[mapping.UUID] = unitid
    handler = await OrgUnitRequestHandler.construct(
        request, mapping.RequestType.REFRESH
    )
    result = await handler.submit()
    return result


def get_details_from_query_args(args):
    arg_map = {
        "minimal": UnitDetails.MINIMAL,
        "nchildren": UnitDetails.NCHILDREN,
        "self": UnitDetails.SELF,
        "full": UnitDetails.FULL,
        "path": UnitDetails.PATH,
    }

    if "details" in args and args["details"] in arg_map:
        return arg_map[args["details"]]
    return UnitDetails.MINIMAL


@router.get("/o/{orgid}/ou/")
async def list_orgunits(
    orgid: UUID,
    start: int | None = 0,
    limit: int | None = 0,
    query: str | None = None,
    root: str | None = None,
    hierarchy_uuids: list[UUID] | None = Query(default=None),
    only_primary_uuid: bool | None = None,
):
    """Query organisational units in an organisation.

    .. :quickref: Unit; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Show the units valid at this point in time,
        in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by units matching this string.

    :>json string items: The returned items.
    :>json string offset: Pagination offset.
    :>json string total: Total number of items available on this query.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.
    :>jsonarr string user_key: Short, unique key identifying the unit.
    :>jsonarr object validity: Validity range of the organisational unit.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     {
       "items": [
         {
           "name": "Hj\u00f8rring b\u00f8rnehus",
           "user_key": "Hj\u00f8rring b\u00f8rnehus",
           "uuid": "391cf990-31a0-5104-8944-6bdc4c934b7a",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         {
           "name": "Hj\u00f8rring skole",
           "user_key": "Hj\u00f8rring skole",
           "uuid": "4b3d0f67-3844-50c3-8332-be3d9819b7be",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         {
           "name": "Hj\u00f8rring skole",
           "user_key": "Hj\u00f8rring skole",
           "uuid": "6d9fcaa1-25cc-587f-acf2-dc02d8e30d76",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         }
       ],
       "offset": 0,
       "total": 4
     }

    """
    orgid = str(orgid)
    c = common.get_connector()

    kwargs = dict(
        limit=limit,
        start=start,
        tilhoerer=orgid,
        gyldighed="Aktiv",
    )

    if query:
        kwargs.update(vilkaarligattr=f"%{query}%")
    if hierarchy_uuids:
        kwargs["opmærkning"] = [str(uuid) for uuid in hierarchy_uuids]

    uuid_filters = []
    if root:
        enheder = await c.organisationenhed.get_all()

        uuids, enheder = unzip(enheder)
        # Fetch parent_uuid from objects
        parent_uuids = map(mapping.PARENT_FIELD.get_uuid, enheder)
        # Create map from uuid --> parent_uuid
        parent_map = dict(zip(uuids, parent_uuids))

        def entry_under_root(uuid):
            """Check whether the given uuid is in the subtree under 'root'.

            Works by recursively ascending the parent_map.

            If the specified root is found, we must have started in its subtree.
            If the specified root is not found, we will stop searching at the
                root of the organisation tree.
            """
            if uuid not in parent_map:
                return False
            return uuid == root or entry_under_root(parent_map[uuid])

        uuid_filters.append(entry_under_root)

    details = get_details_from_query_args(util.get_query_args())

    async def get_minimal_orgunit(*args, **kwargs):
        return await get_one_orgunit(
            *args, details=details, only_primary_uuid=only_primary_uuid, **kwargs
        )

    search_result = await c.organisationenhed.paged_get(
        get_minimal_orgunit, uuid_filters=uuid_filters, **kwargs
    )
    return search_result


@router.get("/o/{orgid}/ou/tree")
async def list_orgunit_tree(
    orgid: UUID,
    query: str | None = None,
    uuid: list[UUID] | None = Query(None),
    only_primary_uuid: bool = False,
):
    """
    Query organisational units in an organisation.

    .. :quickref: Unit; Tree

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Show the units valid at this point in time,
        in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by units matching this string.
    :queryparam uuid uuid: Yield the given units; please note that
                           this overrides any query parameter.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     [
       {
         "children": [
           {
             "name": "Borgmesterens Afdeling",
             "user_key": "Borgmesterens Afdeling",
             "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
             "validity": {
               "from": "1960-01-01",
               "to": null
             }
           }
         ],
         "name": "Hj\u00f8rring Kommune",
         "user_key": "Hj\u00f8rring Kommune",
         "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
         "validity": {
           "from": "1960-01-01",
           "to": null
         }
       },
       {
         "children": [
           {
             "name": "Borgmesterens Afdeling",
             "user_key": "Borgmesterens Afdeling",
             "uuid": "5648c99d-d0f2-52c0-b919-26f16a649f75",
             "validity": {
               "from": "1960-01-01",
               "to": null
             }
           }
         ],
         "name": "L\u00f8norganisation",
         "user_key": "L\u00f8norganisation",
         "uuid": "fb2d158f-114e-5f67-8365-2c520cf10b58",
         "validity": {
           "from": "1960-01-01",
           "to": null
         }
       }
     ]

    """
    orgid = str(orgid)
    c = common.get_connector()

    kwargs = dict(
        tilhoerer=orgid,
        gyldighed="Aktiv",
    )

    if query:
        kwargs.update(vilkaarligattr=f"%{query}%")

    unitids = (
        list(map(str, uuid))
        if uuid is not None
        else (await c.organisationenhed.fetch(**kwargs))
    )

    return await get_unit_tree(c, unitids, only_primary_uuid=only_primary_uuid)


@router.post("/ou/create", status_code=201)
async def create_org_unit(req: dict = Body(...), permissions=Depends(oidc.rbac_owner)):
    """Creates new organisational unit

    .. :quickref: Unit; Create

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: Creation succeeded.

    **Example Request**:

    :<json string name: The name of the org unit
    :<json uuid parent: The parent org unit or organisation
    :<json uuid time_planning: A class identifying the time planning strategy.
    :<json uuid org_unit_type: The type of org unit
    :<json list details: A list of details, see
                         http:get:`/service/(any:type)/(uuid:id)/details/`
    :<json object validity: The validity of the created object.

    The parameter ``org_unit_type`` should contain
    an UUID obtained from the respective facet endpoint.
    See http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

    Validity objects are defined as such:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "name": "Name",
        "parent": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "org_unit_type": {
          "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
        },
        "validity": {
          "from": "2016-01-01",
          "to": null
        },
      }

    :returns: UUID of created org unit

    """

    request = await OrgUnitRequestHandler.construct(req, mapping.RequestType.CREATE)

    return await request.submit()
