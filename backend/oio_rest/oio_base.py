# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Superclasses for OIO objects and object hierarchies."""

import datetime
import json
from abc import ABCMeta
from abc import abstractmethod
from collections import defaultdict
from itertools import filterfalse
from typing import Any
from uuid import UUID

import dateutil
import jsonschema
import more_itertools
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from . import config
from . import db
from . import validate
from .custom_exceptions import BadRequestException
from .custom_exceptions import GoneException
from .custom_exceptions import NotFoundException
from .db import db_helpers
from .db import db_structure
from .db.quick_query.search import quick_search
from .utils import build_registration
from .utils import split_param
from .utils import to_lower_param

"""List of parameters allowed for all searches."""
GENERAL_SEARCH_PARAMS = frozenset(
    {
        "brugerref",
        "foersteresultat",
        "livscykluskode",
        "maximalantalresultater",
        "notetekst",
        "uuid",
        "vilkaarligattr",
        "vilkaarligrel",
        "list",
    }
)

"""List of parameters allowed the apply to temporal operations, i.e.
search and list.

"""
TEMPORALITY_PARAMS = frozenset(
    {
        "registreretfra",
        "registrerettil",
        "registreringstid",
        "virkningfra",
        "virkningtil",
        "virkningstid",
    }
)

"""Parameter used for consolidating virkninger in output. For list, search
and get"""
CONSOLIDATE_PARAM = frozenset(
    {
        "konsolider",
    }
)

"""Some operations take no arguments; this makes it explicit."""
NO_PARAMS = frozenset()


class Searcher(metaclass=ABCMeta):
    @abstractmethod
    async def search_objects(
        self,
        class_name: str,
        uuid: str | UUID | None,
        registration: dict,
        virkning_fra: datetime.datetime | str,
        virkning_til: datetime.datetime | str,
        registreret_fra: datetime.datetime | str | None = None,
        registreret_til: datetime.datetime | str | None = None,
        life_cycle_code=None,
        user_ref=None,
        note=None,
        any_attr_value_arr=None,
        any_rel_uuid_arr=None,
        first_result=None,
        max_results=None,
    ) -> tuple[list[str]]:
        pass


class DefaultSearcher(Searcher):
    @staticmethod
    async def search_objects(
        class_name: str,
        uuid: str | UUID | None,
        registration: dict,
        virkning_fra: datetime.datetime | str,
        virkning_til: datetime.datetime | str,
        registreret_fra: datetime.datetime | str | None = None,
        registreret_til: datetime.datetime | str | None = None,
        life_cycle_code=None,
        user_ref=None,
        note=None,
        any_attr_value_arr=None,
        any_rel_uuid_arr=None,
        first_result=None,
        max_results=None,
    ) -> tuple[list[str]]:
        return await db.search_objects(
            class_name=class_name,
            uuid=uuid,
            registration=registration,
            virkning_fra=virkning_fra,
            virkning_til=virkning_til,
            registreret_fra=registreret_fra,
            registreret_til=registreret_til,
            life_cycle_code=life_cycle_code,
            user_ref=user_ref,
            note=note,
            any_attr_value_arr=any_attr_value_arr,
            any_rel_uuid_arr=any_rel_uuid_arr,
            first_result=first_result,
            max_results=max_results,
        )


class QuickSearcher(Searcher):
    @staticmethod
    async def search_objects(
        class_name: str,
        uuid: str | UUID | None,
        registration: dict,
        virkning_fra: datetime.datetime | str,
        virkning_til: datetime.datetime | str,
        registreret_fra: datetime.datetime | str | None = None,
        registreret_til: datetime.datetime | str | None = None,
        life_cycle_code=None,
        user_ref=None,
        note=None,
        any_attr_value_arr=None,
        any_rel_uuid_arr=None,
        first_result=None,
        max_results=None,
    ) -> tuple[list[str]]:
        try:
            return await quick_search(
                class_name=class_name,
                uuid=uuid,
                registration=registration,
                virkning_fra=virkning_fra,
                virkning_til=virkning_til,
                registreret_fra=registreret_fra,
                registreret_til=registreret_til,
                life_cycle_code=life_cycle_code,
                user_ref=user_ref,
                note=note,
                any_attr_value_arr=any_attr_value_arr,
                any_rel_uuid_arr=any_rel_uuid_arr,
                first_result=first_result,
                max_results=max_results,
            )
        except NotImplementedError:
            return await db.search_objects(
                class_name=class_name,
                uuid=uuid,
                registration=registration,
                virkning_fra=virkning_fra,
                virkning_til=virkning_til,
                registreret_fra=registreret_fra,
                registreret_til=registreret_til,
                life_cycle_code=life_cycle_code,
                user_ref=user_ref,
                note=note,
                any_attr_value_arr=any_attr_value_arr,
                any_rel_uuid_arr=any_rel_uuid_arr,
                first_result=first_result,
                max_results=max_results,
            )


class ConfiguredDBInterface:
    def __init__(self):
        if config.get_settings().quick_search:
            self._searcher: Searcher = QuickSearcher()
        else:
            self._searcher: Searcher = DefaultSearcher()

    @property
    def searcher(self):
        return self._searcher


def typed_get(d, field, default):
    v = d.get(field, default)
    t = type(default)

    if v is None:
        return default

    if not isinstance(v, t):
        raise BadRequestException(
            "expected %s for %r, found %s: %s"
            % (t.__name__, field, type(v).__name__, json.dumps(v))
        )

    return v


def get_virkning_dates(args):
    virkning_fra = args.get("virkningfra")
    virkning_til = args.get("virkningtil")
    virkningstid = args.get("virkningstid")

    if virkningstid:
        if virkning_fra or virkning_til:
            raise BadRequestException(
                "'virkningfra'/'virkningtil' conflict with 'virkningstid'"
            )
        # Timespan has to be non-zero length of time, so we add one
        # microsecond
        dt = dateutil.parser.isoparse(virkningstid)
        virkning_fra = dt
        virkning_til = dt + datetime.timedelta(microseconds=1)
    else:
        if virkning_fra is None and virkning_til is None:
            # TODO: Use the equivalent of TSTZRANGE(current_timestamp,
            # current_timestamp,'[]') if possible
            virkning_fra = datetime.datetime.now()
            virkning_til = virkning_fra + datetime.timedelta(microseconds=1)
    return virkning_fra, virkning_til


def get_registreret_dates(args):
    registreret_fra = args.get("registreretfra")
    registreret_til = args.get("registrerettil")
    registreringstid = args.get("registreringstid")

    if registreringstid:
        if registreret_fra or registreret_til:
            raise BadRequestException(
                "'registreretfra'/'registrerettil' conflict with 'registreringstid'"
            )
        else:
            # Timespan has to be non-zero length of time, so we add one
            # microsecond
            dt = dateutil.parser.isoparse(registreringstid)
            registreret_fra = dt
            registreret_til = dt + datetime.timedelta(microseconds=1)
    return registreret_fra, registreret_til


def _remove_deleted(objects):
    """Remove deleted objects from results."""
    if objects is None:
        return None

    def is_deleted(obj) -> bool:
        """Return whether the object is deleted or not."""
        if not isinstance(obj, list):
            return False
        livscykluskode = obj[0]["registreringer"][0]["livscykluskode"]
        return livscykluskode == db.Livscyklus.SLETTET.value

    return list(filterfalse(is_deleted, objects))


class Registration:
    def __init__(self, oio_class, states, attributes, relations):
        self.oio_class = oio_class
        self.states = states
        self.attributes = attributes
        self.relations = relations


class OIOStandardHierarchy:
    """Implement API for entire hierarchy."""

    _name = ""
    _classes = []

    @classmethod
    def setup_api(cls):
        """Set up API for the classes included in the hierarchy.

        Note that version number etc. may have to be added to the URL."""

        assert cls._name and cls._classes, "hierarchy not configured?"

        oio_router = APIRouter()

        for c in cls._classes:
            router = c.create_api(cls._name)
            oio_router.include_router(router)

        hierarchy = cls._name.lower()
        classes_url = "/{}/{}".format(hierarchy, "classes")

        @oio_router.get(classes_url, name="_".join([hierarchy, "classes"]))
        async def get_classes():
            """Return the classes including their fields under this service.

            .. :quickref: :http:get:`/(service)/classes`

            """
            structure = db_structure.REAL_DB_STRUCTURE
            clsnms = [c.__name__.lower() for c in cls._classes]
            hierarchy_dict = {c: structure[c] for c in clsnms}
            return hierarchy_dict

        return oio_router


async def _get_json_from_request(request: Request):
    """Return the JSON input from the request.

    The JSON input typically comes from the body of the request with
    Content-Type: application/json. However, for POST/PUT operations
    involving multipart/form-data, the JSON input is expected to be
    contained in a form field called 'json'. This method handles this in a
    consistent way.
    """
    try:
        return await request.json()
    except json.decoder.JSONDecodeError:
        formset = await request.form()
        data = formset.get("json", None)
        if data is not None:
            try:
                return json.loads(data)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail={"message": "unparsable json"}
                )
        else:
            return None


async def _get_args_from_request(request: Request):
    """Get args from request.

    If supplied, arguments will be extracted from the json body of GET requests.
    """
    if request.method == "GET" and await request.body():
        json_body: dict[str, Any] = await request.json()
        # Flatten into list of two-tuples, as required by ArgumentDict
        return list(
            (key, value)
            for key, values in json_body.items()
            for value in more_itertools.collapse(values)
        )
    return request.query_params.multi_items()


def _process_args(args, as_lists: bool = False) -> dict:
    """Convert arguments to lowercase, optionally getting them as lists."""
    args_dict = defaultdict(list)
    for key, value in args:
        key = to_lower_param(key)
        if key == "bvn":
            key = "brugervendtnoegle"
        args_dict[key].append(value)

    if as_lists:
        return dict(args_dict)
    return {k: more_itertools.first(v) for k, v in args_dict.items()}


class OIORestObject:
    """
    Implement an OIO object - manage access to database layer for this object.

    This class is intended to be subclassed, but not to be initialized.
    """

    # The name of the current service. This is set by the create_api() method.
    service_name = None

    @classmethod
    async def create_object_direct(cls, input, args):
        """A :ref:`CreateOperation` that creates a new object from the JSON
        payload. It returns a newly generated UUID for the created object.

        .. :quickref: :ref:`CreateOperation`

        """
        args = _process_args(args)
        await cls.verify_args(args)

        # Validate JSON input
        if not input:
            raise HTTPException(status_code=400, detail={"uuid": None})
        try:
            validate.validate(input, cls.__name__.lower())
        except jsonschema.exceptions.ValidationError as e:
            raise HTTPException(status_code=400, detail={"message": e.message})

        note = typed_get(input, "note", "")
        registration = cls.gather_registration(input)
        uuid = await db.create_or_import_object(cls.__name__, note, registration)
        # Pass log info on request object.
        # request.api_operation = "Opret"
        # request.uuid = uuid
        return {"uuid": uuid}

    @classmethod
    async def create_object(cls, request: Request):
        args = await _get_args_from_request(request)
        input = await _get_json_from_request(request)
        return await cls.create_object_direct(input, args)

    @classmethod
    async def get_objects_direct(cls, raw_args):
        """A :ref:`ListOperation` or :ref:`SearchOperation` depending on parameters.

        With any the of ``uuid``, ``virking*`` and ``registeret*`` parameters,
        it is a :ref:`ListOperation` and will return one or more whole JSON
        objects.

        Given any other parameters, the operation is a :ref:`SearchOperation`
        and will only return a list of UUIDs to the objects.

        .. :quickref: :ref:`ListOperation` or :ref:`SearchOperation`

        """
        list_args = _process_args(raw_args, as_lists=True)
        args = _process_args(raw_args)
        await cls.verify_args(args, search=True, temporality=True, consolidate=True)

        registreret_fra, registreret_til = get_registreret_dates(args)
        virkning_fra, virkning_til = get_virkning_dates(args)

        uuid_param = list_args.get("uuid")

        consolidate_param = list_args.get("konsolider") is not None
        if consolidate_param:
            list_fn = db.list_and_consolidate_objects
        else:
            list_fn = db.list_objects

        valid_list_args = TEMPORALITY_PARAMS | CONSOLIDATE_PARAM | {"uuid"}

        # Assume the search operation if other params were specified or the
        # 'list' parameter is specified
        if not (valid_list_args.issuperset(args) and args.get("list") is None):
            # Only one uuid is supported through the search operation
            if uuid_param is not None and len(uuid_param) > 1:
                raise BadRequestException(
                    "Multiple uuid parameters passed "
                    "to search operation. Only one "
                    "uuid parameter is supported."
                )
            uuid_param = args.get("uuid")
            first_result = args.get("foersteresultat")
            if first_result is not None:
                first_result = int(first_result)
            max_results = args.get("maximalantalresultater")
            if max_results is not None:
                max_results = int(max_results)

            any_attr_value_arr = list_args.get("vilkaarligattr")
            any_rel_uuid_arr = list_args.get("vilkaarligrel")
            life_cycle_code = args.get("livscykluskode")
            user_ref = args.get("brugerref")
            note = args.get("notetekst")

            # Fill out a registration object based on the query arguments
            registration = build_registration(cls.__name__, list_args)
            # request.api_operation = "Søg"
            results = await ConfiguredDBInterface().searcher.search_objects(
                class_name=cls.__name__,
                uuid=uuid_param,
                registration=registration,
                virkning_fra=virkning_fra,
                virkning_til=virkning_til,
                registreret_fra=registreret_fra,
                registreret_til=registreret_til,
                life_cycle_code=life_cycle_code,
                user_ref=user_ref,
                note=note,
                any_attr_value_arr=any_attr_value_arr,
                any_rel_uuid_arr=any_rel_uuid_arr,
                first_result=first_result,
                max_results=max_results,
            )

            if args.get("list") is not None:
                # request.api_operation = "List"
                results = await list_fn(
                    cls.__name__,
                    results[0],
                    virkning_fra,
                    virkning_til,
                    registreret_fra,
                    registreret_til,
                )
                results = _remove_deleted(results)

        else:
            uuid_param = list_args.get("uuid")
            # request.api_operation = "List"
            results = await list_fn(
                cls.__name__,
                uuid_param,
                virkning_fra,
                virkning_til,
                registreret_fra,
                registreret_til,
            )
            results = _remove_deleted(results)

        if results is None:
            results = []
        # if uuid_param:
        #    request.uuid = uuid_param
        # else:
        #    request.uuid = ""
        return {"results": results}

    @classmethod
    async def get_objects(cls, request: Request):
        # Convert arguments to lowercase, getting them as lists
        raw_args = await _get_args_from_request(request)
        return await cls.get_objects_direct(raw_args)

    @classmethod
    async def get_object_direct(cls, uuid: UUID, args):
        """A :ref:`ReadOperation`. Return a single whole object as a JSON object.

        .. :quickref: :ref:`ReadOperation`

        """
        args = _process_args(args)
        await cls.verify_args(args, temporality=True, consolidate=True)

        uuid = str(uuid)

        registreret_fra, registreret_til = get_registreret_dates(args)

        virkning_fra, virkning_til = get_virkning_dates(args)

        consolidate_param = args.get("konsolider") is not None
        if consolidate_param:
            list_fn = db.list_and_consolidate_objects
        else:
            list_fn = db.list_objects

        # request.api_operation = "Læs"
        # request.uuid = uuid
        object_list = await list_fn(
            cls.__name__,
            [uuid],
            virkning_fra,
            virkning_til,
            registreret_fra,
            registreret_til,
        )
        try:
            object = object_list[0]
        except IndexError:
            # No object found with that ID.
            raise NotFoundException(
                "No {} with ID {} found in service {}".format(
                    cls.__name__, uuid, cls.service_name
                )
            )
        # Raise 410 Gone if object is deleted.
        if (
            object[0]["registreringer"][0]["livscykluskode"]
            == db.Livscyklus.SLETTET.value
        ):
            raise GoneException("This object has been deleted.")
        return {uuid: object}

    @classmethod
    async def get_object(cls, uuid: UUID, request: Request):
        args = await _get_args_from_request(request)
        return await cls.get_object_direct(uuid, args)

    @classmethod
    def gather_registration(cls, input):
        """Return a registration dict from the input dict."""
        attributes = typed_get(input, "attributter", {})
        states = typed_get(input, "tilstande", {})

        relations = typed_get(input, "relationer", {})
        filtered_relations = {key: val for key, val in relations.items() if val}

        return {
            "states": states,
            "attributes": attributes,
            "relations": filtered_relations,
        }

    @classmethod
    async def put_object_direct(cls, uuid: UUID, input, args):
        """A :ref:`ImportOperation` that creates or overwrites an object from
        the JSON payload.  It returns the UUID for the object.

        If there is no object with the UUID or the object with that UUID was
        :ref:`deleted <DeleteOperation>` or :ref:`passivated
        <PassivateOperation>`, it creates a new object at the specified UUID.
        It sets ``livscykluskode: "Importeret"``.

        If an object with the UUID exists, it completely overwrites the object
        including all ``virkning`` periods. It sets
        ``livscykluskode: "Rettet"``.

        .. :quickref: :ref:`ImportOperation`

        """
        args = _process_args(args)
        await cls.verify_args(args)

        uuid = str(uuid)
        if not input:
            raise HTTPException(status_code=400, detail={"uuid": None})

        # Validate JSON input
        try:
            validate.validate(input, cls.__name__.lower())
        except jsonschema.exceptions.ValidationError as e:
            raise HTTPException(status_code=400, detail={"message": e.message})

        # Get most common parameters if available.
        note = typed_get(input, "note", "")
        registration = cls.gather_registration(input)
        exists = await db.object_exists(cls.__name__, str(uuid))
        deleted_or_passive = False
        if exists:
            livscyklus = await db.get_life_cycle_code(cls.__name__, uuid)
            if livscyklus in (
                db.Livscyklus.PASSIVERET.value,
                db.Livscyklus.SLETTET.value,
            ):
                deleted_or_passive = True

        # request.uuid = uuid

        if not exists:
            # Do import.
            # request.api_operation = "Import"
            await db.create_or_import_object(cls.__name__, note, registration, uuid)
        elif deleted_or_passive:
            # Import.
            # request.api_operation = "Import"
            await db.update_object(
                cls.__name__,
                note,
                registration,
                uuid=uuid,
                life_cycle_code=db.Livscyklus.IMPORTERET.value,
            )
        else:
            # Edit.
            # request.api_operation = "Ret"
            await db.create_or_import_object(cls.__name__, note, registration, uuid)
        return {"uuid": uuid}

    @classmethod
    async def put_object(cls, uuid: UUID, request: Request):
        args = await _get_args_from_request(request)
        input = await _get_json_from_request(request)
        return await cls.put_object_direct(uuid, input, args)

    @classmethod
    async def patch_object_direct(cls, uuid: UUID, input):
        """An :ref:`UpdateOperation` or :ref:`PassivateOperation`. Apply the
        JSON payload as a change to the object. Return the UUID of the object.

        If ``livscyklus: "Passiv"`` is set it is a :ref:`PassivateOperation`.

        .. :quickref: :ref:`UpdateOperation` or :ref:`PassivateOperation`

        """
        # TODO: Why no cls.verify_args here
        uuid = str(uuid)

        # If the object doesn't exist, we can't patch it.
        if not await db.object_exists(cls.__name__, uuid):
            raise NotFoundException(
                "No {} with ID {} found in service {}".format(
                    cls.__name__, uuid, cls.service_name
                )
            )

        if not input:
            raise HTTPException(status_code=400, detail={"uuid": None})

        # Get most common parameters if available.
        note = typed_get(input, "note", "")
        registration = cls.gather_registration(input)

        # Validate JSON input
        try:
            validate.validate(input, cls.__name__.lower(), do_create=False)
        except jsonschema.exceptions.ValidationError as e:
            raise HTTPException(status_code=400, detail={"message": e.message})

        if typed_get(input, "livscyklus", "").lower() == "passiv":
            # Passivate
            # request.api_operation = "Passiver"
            registration = cls.gather_registration({})
            await db.passivate_object(cls.__name__, note, registration, uuid)
        else:
            # Edit/change
            # request.api_operation = "Ret"
            await db.update_object(cls.__name__, note, registration, uuid)
        return {"uuid": uuid}

    @classmethod
    async def patch_object(cls, uuid: UUID, request: Request):
        # TODO: Why no cls.verify_args here
        uuid = str(uuid)
        input = await _get_json_from_request(request)
        return await cls.patch_object_direct(uuid, input)

    @classmethod
    async def delete_object_direct(cls, uuid: UUID, input):
        """A :ref:`DeleteOperation`. Delete the object and return the UUID.

        .. :quickref: :ref:`DeleteOperation`

        """
        uuid = str(uuid)

        note = typed_get(input, "note", "")
        class_name = cls.__name__
        # Gather a blank registration
        registration = cls.gather_registration({})
        # request.api_operation = "Slet"
        # request.uuid = uuid
        await db.delete_object(class_name, registration, note, uuid)

        return {"uuid": uuid}

    @classmethod
    async def delete_object(cls, uuid: UUID, request: Request):
        """A :ref:`DeleteOperation`. Delete the object and return the UUID.

        .. :quickref: :ref:`DeleteOperation`

        """
        await cls.verify_args(_process_args(await _get_args_from_request(request)))
        input = (await _get_json_from_request(request)) or {}
        return await cls.delete_object_direct(uuid, input)

    @classmethod
    async def get_fields(cls, request: Request):
        """Return a list of all fields a given object has.

        .. :quickref: :http:get:`/(service)/(object)/fields`

        """

        """Set up API with correct database access functions."""
        await cls.verify_args(_process_args(await _get_args_from_request(request)))
        structure = db_structure.REAL_DB_STRUCTURE
        class_key = cls.__name__.lower()
        # TODO: Perform some transformations to improve readability.
        class_dict = structure[class_key]
        return class_dict

    @classmethod
    async def get_schema(cls):
        """Returns the JSON schema of an object.

        .. :quickref: :http:get:`/(service)/(object)/schema`

        """
        return validate.get_schema(cls.__name__.lower())

    @classmethod
    def create_api(cls, hierarchy):
        """Set up API with correct database access functions."""
        cls.service_name = hierarchy
        hierarchy = hierarchy.lower()
        class_name = cls.__name__.lower()
        class_url = f"/{hierarchy}/{class_name}"
        cls_fields_url = "{}/{}".format(class_url, "fields")
        object_url = class_url + "/{uuid}"

        rest_router = APIRouter()

        rest_router.get(class_url, name="_".join([cls.__name__, "get_objects"]))(
            cls.get_objects
        )
        rest_router.post(
            class_url, name="_".join([cls.__name__, "create_object"]), status_code=201
        )(cls.create_object)

        # Structure URLs
        rest_router.get(cls_fields_url, name="_".join([cls.__name__, "fields"]))(
            cls.get_fields
        )
        # JSON schemas
        rest_router.get(
            "{}/{}".format(class_url, "schema"),
            name="_".join([cls.__name__, "schema"]),
        )(cls.get_schema)

        rest_router.get(object_url, name="_".join([cls.__name__, "get_object"]))(
            cls.get_object
        )
        rest_router.put(object_url, name="_".join([cls.__name__, "put_object"]))(
            cls.put_object
        )
        rest_router.patch(object_url, name="_".join([cls.__name__, "patch_object"]))(
            cls.patch_object
        )
        rest_router.delete(
            object_url, name="_".join([cls.__name__, "delete_object"]), status_code=202
        )(cls.delete_object)

        return rest_router

    # Templates which may be overridden on subclass.
    # Templates may only be overridden on subclass if they are explicitly
    # listed here.
    RELATIONS_TEMPLATE = "relations_array.sql"

    @classmethod
    def attribute_names(cls):
        return {
            a
            for attr in db_helpers.get_attribute_names(cls.__name__)
            for a in db_helpers.get_attribute_fields(attr)
        }

    @classmethod
    def relation_names(cls):
        return set(db_helpers.get_relation_names(cls.__name__))

    @classmethod
    def state_names(cls):
        return set(db_helpers.get_state_names(cls.__name__))

    @classmethod
    async def verify_args(
        cls,
        args,
        temporality=False,
        search=False,
        consolidate=False,
    ):
        req_args = set(args)

        if temporality:
            req_args -= TEMPORALITY_PARAMS

        if consolidate:
            req_args -= CONSOLIDATE_PARAM

        if search:
            req_args -= GENERAL_SEARCH_PARAMS
            req_args -= TEMPORALITY_PARAMS
            req_args -= cls.attribute_names()
            req_args -= cls.state_names()

            # special handling of argument with an object type
            req_args -= {
                a for a in req_args if split_param(a)[0] in cls.relation_names()
            }

        if req_args:
            arg_string = ", ".join(sorted(req_args))
            raise BadRequestException(f"Unsupported argument(s): {arg_string}")
