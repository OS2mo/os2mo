# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Employees
---------

This section describes how to interact with employees.

For more information regarding reading relations involving employees, refer to
http:get:`/service/(any:type)/(uuid:id)/details/`

"""
import copy
import enum
import logging
from datetime import date
from functools import partial
from operator import contains
from operator import itemgetter
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Query

from . import autocomplete
from . import handlers
from . import org
from .. import common
from .. import config
from .. import depends
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..graphapi.middleware import is_graphql
from ..lora import LoraObjectType
from ..triggers import Trigger
from .validation.validator import does_employee_with_cpr_already_exist
from mora.auth.keycloak import oidc
from mora.request_scoped.bulking import get_lora_object
from ramodels.base import tz_isodate


router = APIRouter()

logger = logging.getLogger(__name__)


@enum.unique
class EmployeeDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with everything except child count
    FULL = 1


class EmployeeRequestHandler(handlers.RequestHandler):
    role_type = "employee"

    async def prepare_create(self, req):
        name = util.checked_get(req, mapping.NAME, "", required=False)
        givenname = util.checked_get(req, mapping.GIVENNAME, "", required=False)
        surname = util.checked_get(req, mapping.SURNAME, "", required=False)

        if name and (surname or givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either name or given name/surame"
            )

        if name:
            givenname = name.rsplit(" ", maxsplit=1)[0]
            surname = name[len(givenname) :].strip()

        if (not name) and (not givenname) and (not surname):
            raise exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
                name="Missing name or givenname or surname"
            )

        nickname_givenname, nickname_surname = self._handle_nickname(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        cpr = util.checked_get(req, mapping.CPR_NO, "", required=False)
        userid = util.get_uuid(req, required=False) or str(uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, userid)
        seniority = req.get(mapping.SENIORITY, None)
        # parse seniority
        if seniority is not None:
            seniority = tz_isodate(seniority).strftime("%Y-%m-%d")

        if cpr:
            try:
                valid_from = util.get_cpr_birthdate(cpr)
            except ValueError as exc:
                settings = config.get_settings()
                if settings.cpr_validate_birthdate:
                    exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr, cause=exc)
                else:
                    valid_from = util.NEGATIVE_INFINITY
        else:
            valid_from = util.NEGATIVE_INFINITY

        valid_to = util.POSITIVE_INFINITY

        if cpr and (
            await does_employee_with_cpr_already_exist(
                cpr, valid_from, valid_to, org_uuid, userid
            )
        ):
            raise exceptions.HTTPException(exceptions.ErrorCodes.V_EXISTING_CPR)

        user = common.create_bruger_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            fornavn=givenname,
            efternavn=surname,
            kaldenavn_fornavn=nickname_givenname,
            kaldenavn_efternavn=nickname_surname,
            seniority=seniority,
            brugervendtnoegle=bvn,
            tilhoerer=org_uuid,
            cpr=cpr,
        )

        details = util.checked_get(req, "details", [])

        # Validate the creation requests as groups (one group for each role/detail type)
        await self.validate_detail_requests_as_groups(details)

        # Validate the creation requests individually
        details_with_persons = _inject_persons(details, userid, valid_from, valid_to)
        self.details_requests = await handlers.generate_requests(
            details_with_persons, mapping.RequestType.CREATE
        )

        self.payload = user
        self.uuid = userid
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = userid

    def _handle_nickname(self, obj: dict[str | Any, Any]):
        nickname_givenname = obj.get(mapping.NICKNAME_GIVENNAME)
        nickname_surname = obj.get(mapping.NICKNAME_SURNAME)
        nickname = obj.get(mapping.NICKNAME)

        if nickname and (nickname_surname or nickname_givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either nickname or given nickname/surname"
            )
        if nickname:
            nickname_givenname = nickname.rsplit(" ", maxsplit=1)[0]
            nickname_surname = nickname[len(nickname_givenname) :].strip()

        return nickname_givenname, nickname_surname

    async def prepare_edit(self, req: dict):
        original_data = util.checked_get(req, "original", {}, required=False)
        data = util.checked_get(req, "data", {}, required=True)
        userid = util.get_uuid(req, required=False)
        if not userid:
            userid = util.get_uuid(data, fallback=original_data)

        # Get the current org-unit which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.bruger.get(uuid=userid)
        new_from, new_to = util.get_validities(data)

        payload = {"note": "Rediger medarbejder"}

        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "brugergyldighed"),
            )

            original_uuid = util.get_mapping_uuid(original_data, mapping.EMPLOYEE)

            if original_uuid and original_uuid != userid:
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    "cannot change employee uuid!",
                )

        update_fields = []

        # Always update gyldighed
        update_fields.append((mapping.EMPLOYEE_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

        changed_props = {}
        changed_extended_props = {}

        if mapping.USER_KEY in data:
            changed_props["brugervendtnoegle"] = data[mapping.USER_KEY]

        givenname = data.get(mapping.GIVENNAME, "")
        surname = data.get(mapping.SURNAME, "")
        name = data.get(mapping.NAME, "")

        if name and (surname or givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either name or given name/surame"
            )
        if name:
            givenname = name.rsplit(" ", maxsplit=1)[0]
            surname = name[len(givenname) :].strip()

        if givenname:
            changed_extended_props["fornavn"] = givenname
        if surname:
            changed_extended_props["efternavn"] = surname

        nickname_givenname, nickname_surname = self._handle_nickname(data)

        seniority = data.get(mapping.SENIORITY)

        # clear rather than skip if exists, but value is None
        if seniority is None and mapping.SENIORITY in data:
            seniority = ""

        if nickname_givenname is not None:
            changed_extended_props["kaldenavn_fornavn"] = nickname_givenname
        if nickname_surname is not None:
            changed_extended_props["kaldenavn_efternavn"] = nickname_surname
        if seniority is not None:
            changed_extended_props["seniority"] = seniority

        if changed_props:
            update_fields.append(
                (
                    mapping.EMPLOYEE_EGENSKABER_FIELD,
                    changed_props,
                )
            )

        if changed_extended_props:
            update_fields.append(
                (
                    mapping.EMPLOYEE_UDVIDELSER_FIELD,
                    changed_extended_props,
                )
            )

        if mapping.CPR_NO in data:
            related = mapping.EMPLOYEE_PERSON_FIELD.get(original)
            if related and len(related) > 0:
                attrs = related[-1].copy()
                attrs["urn"] = f"urn:dk:cpr:person:{data[mapping.CPR_NO]}"
                update_fields.append((mapping.EMPLOYEE_PERSON_FIELD, attrs))
            else:
                attrs = {}
                attrs["urn"] = f"urn:dk:cpr:person:{data[mapping.CPR_NO]}"
                update_fields.append((mapping.EMPLOYEE_PERSON_FIELD, attrs))

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.EMPLOYEE_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )
        self.payload = payload
        self.uuid = userid
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = userid

    async def submit(self):
        c = lora.Connector()

        if self.request_type == mapping.RequestType.CREATE:
            self.result = await c.bruger.create(self.payload, self.uuid)
        else:
            self.result = await c.bruger.update(self.payload, self.uuid)

        # process subrequests, if any
        [await r.submit() for r in getattr(self, "details_requests", [])]

        return await super().submit()


async def request_bulked_get_one_employee(
    userid: str,
    details: EmployeeDetails = EmployeeDetails.MINIMAL,
    only_primary_uuid: bool = False,
):
    connector = common.get_connector()
    return await get_one_employee(
        c=connector,
        userid=userid,
        user=await get_lora_object(
            type_=LoraObjectType.user, uuid=userid, connector=connector
        )
        if not only_primary_uuid
        else None,
        details=details,
        only_primary_uuid=only_primary_uuid,
    )


async def get_one_employee(
    c: lora.Connector,
    userid,
    user: dict[str, Any] | None = None,
    details=EmployeeDetails.MINIMAL,
    only_primary_uuid: bool = False,
):
    if not user:
        user = await c.bruger.get(userid)

        if not user or not util.is_reg_valid(user):
            return None

    if only_primary_uuid:
        # This block could be before the user check, so we would not have to contact
        # LoRa as we can construct the output without during so, however we need to
        # actually validate that the user actually exists to avoid false information.
        return {mapping.UUID: userid}

    props = user["attributter"]["brugeregenskaber"][0]
    extensions = user["attributter"]["brugerudvidelser"][0]

    fornavn = extensions.get("fornavn", "")
    efternavn = extensions.get("efternavn", "")
    kaldenavn_fornavn = extensions.get("kaldenavn_fornavn", "")
    kaldenavn_efternavn = extensions.get("kaldenavn_efternavn", "")
    seniority = extensions.get(mapping.SENIORITY, None)

    r = {
        mapping.GIVENNAME: fornavn,
        mapping.SURNAME: efternavn,
        mapping.NAME: " ".join((fornavn, efternavn)),
        mapping.NICKNAME_GIVENNAME: kaldenavn_fornavn,
        mapping.NICKNAME_SURNAME: kaldenavn_efternavn,
        mapping.NICKNAME: " ".join((kaldenavn_fornavn, kaldenavn_efternavn)).strip(),
        mapping.UUID: userid,
        mapping.SENIORITY: seniority,
    }
    if is_graphql():
        rels = user["relationer"]

        if rels.get("tilknyttedepersoner"):
            cpr = rels["tilknyttedepersoner"][0]["urn"].rsplit(":", 1)[-1]
            r[mapping.CPR_NO] = cpr

        r[mapping.USER_KEY] = props.get("brugervendtnoegle", "")

    if details is EmployeeDetails.FULL:
        rels = user["relationer"]

        if rels.get("tilknyttedepersoner"):
            cpr = rels["tilknyttedepersoner"][0]["urn"].rsplit(":", 1)[-1]
            r[mapping.CPR_NO] = cpr

        r[mapping.ORG] = await org.get_configured_organisation()
        r[mapping.USER_KEY] = props.get("brugervendtnoegle", "")
    elif details is EmployeeDetails.MINIMAL:
        pass  # already done
    return r


@router.get(
    "/e/autocomplete/",
    responses={
        "400": {"description": "Invalid input"},
    },
)
# async def autocomplete_employees(query: str):
async def autocomplete_employees(
    session: depends.Session,
    query: str,
    at: date
    | None = Query(
        None,
        description='The "at date" to use, e.g. `2020-01-31`. '
        "Results are only included if they are active at the specified date.",
    ),
):
    settings = config.get_settings()
    if settings.confdb_autocomplete_v2_use_legacy:
        logger.debug("using autocomplete_employee_v2 legacy")
        return await autocomplete.get_results(
            "bruger", settings.confdb_autocomplete_attrs_employee, query
        )

    logger.debug("using autocomplete_employee_v2 new")
    search_results = await autocomplete.search_employees(session, query, at)

    # Decorate search results with data through GraphQL
    return {
        "items": await autocomplete.decorate_employee_search_result(
            settings, search_results, at
        )
    }


@router.get(
    "/o/{orgid}/e/",
    responses={
        "400": {"description": "Invalid input"},
    },
)
# @util.restrictargs('at', 'start', 'limit', 'query', 'associated')
async def list_employees(
    orgid: UUID,
    start: int | None = 0,
    limit: int | None = 0,
    query: str | None = None,
    associated: bool | None = None,
    only_primary_uuid: bool | None = None,
):
    """Query employees in an organisation.

    .. :quickref: Employee; List & search

    :param uuid orgid: UUID of the organisation to search.
        Note: This parameter is now deprecated, and does not affect the result.

    :queryparam date at: Show employees at this point in time,
        in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by employees matching this string.
        Please note that this only applies to attributes of the user, not the
        relations or engagements they have.

    :>json string items: The returned items.
    :>json string offset: Pagination offset.
    :>json string total: Total number of items available on this query.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     {
       "items": [
         {
           "name": "Knud S\u00f8lvtoft Pedersen",
           "uuid": "059b45b4-7e92-4450-b7ae-dff989d66ad2"
         },
         {
           "name": "Hanna Hede Pedersen",
           "uuid": "74894be9-2476-48e2-8b3a-ba1db926bb0b"
         },
         {
           "name": "Susanne Nybo Pedersen",
           "uuid": "7e79881d-a4ee-4654-904e-4aaa0d697157"
         },
         {
           "name": "Bente Pedersen",
           "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
         },
         {
           "name": "Vang Overgaard Pedersen",
           "uuid": "f2b9008d-8646-4672-8a91-c12fa897f9a6"
         }
       ],
       "offset": 0,
       "total": 5
     }

    """
    orgid = str(orgid)

    # TODO: share code with list_orgunits?

    c = common.get_connector()

    kwargs = dict(
        limit=limit,
        start=start,
        gyldighed="Aktiv",
    )

    if query:
        if util.is_cpr_number(query):
            kwargs.update(
                tilknyttedepersoner="urn:dk:cpr:person:" + query,
            )
        else:
            query = query
            query = query.split(" ")
            for i in range(0, len(query)):
                query[i] = "%" + query[i] + "%"
            kwargs["vilkaarligattr"] = query

    uuid_filters = []
    # Filter search_result to only show employees with associations
    if associated:
        # NOTE: This call takes ~500ms on fixture-data
        assocs = await c.organisationfunktion.get_all(funktionsnavn="Tilknytning")
        assocs = map(itemgetter(1), assocs)
        assocs = set(map(mapping.USER_FIELD.get_uuid, assocs))
        uuid_filters.append(partial(contains, assocs))

    async def get_full_employee(*args, **kwargs):
        return await get_one_employee(
            *args,
            **kwargs,
            details=EmployeeDetails.FULL,
            only_primary_uuid=only_primary_uuid,
        )

    search_result = await c.bruger.paged_get(
        get_full_employee, uuid_filters=uuid_filters, **kwargs
    )
    return search_result


# When RBAC enabled: currently, only the admin role can create employees
@router.post("/e/create", status_code=201)
async def create_employee(req: dict = Body(...), permissions=Depends(oidc.rbac_admin)):
    """Create a new employee

    .. :quickref: Employee; Create

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: Creation succeeded.

    **Example Request**:

    :<json string name: Name of the employee.
    :<json string givenname: Given name of the employee.
    :<json string surname: Surname of the employee.
    :<json string nickname: Nickname of the employee.
    :<json string nickname_givenname: The given name part of the nickname.
    :<json string nickname_surname: The surname part of the nickname.
    :<json string cpr_no: The CPR no of the employee
    :<json string user_key: Short, unique key identifying the employee.
    :<json object org: The organisation with which the employee is associated
    :<json string uuid: An **optional** parameter, that will be used as the
      UUID for the employee.
    :<json list details: A list of details to be created for the employee.

    For both the name and the nickname, only the full name or
    givenname/surname should be given, not both.
    If only the full name is supplied, the name will be split on the last
    space.

    For more information on the available details,
    see: http:post:`/service/details/create`.
    Note, that the ``person`` parameter is implicit in these payload, and
    should not be given.

    .. sourcecode:: json

      {
        "name": "Name Name",
        "nickname": "Nickname Whatever",
        "cpr_no": "0101501234",
        "user_key": "1234",
        "org": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f",
        "details": [
          {
            "type": "engagement",
            "org_unit": {
              "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
            },
            "job_function": {
              "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
            },
            "engagement_type": {
              "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
            },
            "validity": {
                "from": "2016-01-01",
                "to": "2017-12-31"
            }
          }
        ]
      }

    :returns: UUID of created employee

    """
    request = await EmployeeRequestHandler.construct(req, mapping.RequestType.CREATE)
    return await request.submit()


def _inject_persons(details, employee_uuid, valid_from, valid_to):
    decorated = copy.deepcopy(details)
    for detail in decorated:
        detail["person"] = {
            mapping.UUID: employee_uuid,
            mapping.VALID_FROM: valid_from,
            mapping.VALID_TO: valid_to,
            "allow_nonexistent": True,
        }

    return decorated
