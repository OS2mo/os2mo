# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''This module provides infrastructure for registering and invoking
handlers for the various detail types.

'''

import abc
import inspect
import typing

from structlog import get_logger

from mora.async_util import async_to_sync
from mora.async_util import in_separate_thread
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..mapping import EventType, RequestType
from ..triggers import Trigger

# The handler mappings are populated by each individual active
# RequestHandler
HANDLERS_BY_ROLE_TYPE = {}
HANDLERS_BY_FUNCTION_KEY = {}
FUNCTION_KEYS = {}

logger = get_logger()


class _RequestHandlerMeta(abc.ABCMeta):
    '''Metaclass for automatically registering handlers

    '''

    @staticmethod
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        if not inspect.isabstract(cls):
            cls._register()

        return cls


class RequestHandler(metaclass=_RequestHandlerMeta):
    '''Abstract base class for automatically registering handlers for
    details. Subclass are automatically registered once they
    implements all relevant methods, i.e. they're no longer abstract.

    '''
    role_type = None
    '''
    The `role_type` for corresponding details to this attribute.
    '''

    @classmethod
    def _register(cls):
        assert cls.role_type is not None
        assert cls.role_type not in HANDLERS_BY_ROLE_TYPE

        HANDLERS_BY_ROLE_TYPE[cls.role_type] = cls

    def __init__(
        self, request: dict, request_type: RequestType, sync_construct: bool = True
    ):
        """
        Initialize a request, and perform all required validation.

        :param request: A dict containing a request
        :param request_type: An instance of :class:`RequestType`.
        """
        super().__init__()
        self.request_type = request_type
        self.request = request
        self.payload = None
        self.uuid = None
        self.trigger_results_before = None
        self.trigger_results_after = None

        self.trigger_dict = {
            Trigger.REQUEST_TYPE: request_type,
            Trigger.REQUEST: request,
            Trigger.ROLE_TYPE: self.role_type,
            Trigger.EVENT_TYPE: EventType.ON_BEFORE
        }
        if sync_construct:
            self._sync_construct()

    def _sync_construct(self):
        if self.request_type == RequestType.CREATE:
            self.prepare_create(self.request)
        elif self.request_type == RequestType.EDIT:
            self.prepare_edit(self.request)
        elif self.request_type == RequestType.TERMINATE:
            self.prepare_terminate(self.request)
        elif self.request_type == RequestType.REFRESH:
            self.prepare_refresh(self.request)
        else:
            raise NotImplementedError

        self.trigger_dict.update({
            Trigger.UUID: self.trigger_dict.get(Trigger.UUID, "") or self.uuid
        })
        self.trigger_results_before = None
        if not util.get_args_flag("triggerless"):
            self.trigger_results_before = in_separate_thread(
                async_to_sync(Trigger.run)
            )(
                self.trigger_dict
            )

    @classmethod
    async def construct(cls, *args, **kwargs):
        obj = cls(*args, **kwargs, sync_construct=False)

        if obj.request_type == RequestType.CREATE:
            await obj.aprepare_create(obj.request)
        elif obj.request_type == RequestType.EDIT:
            await obj.aprepare_edit(obj.request)
        elif obj.request_type == RequestType.TERMINATE:
            await obj.aprepare_terminate(obj.request)
        elif obj.request_type == RequestType.REFRESH:
            await obj.aprepare_refresh(obj.request)
        else:
            raise NotImplementedError

        obj.trigger_dict.update({
            Trigger.UUID: obj.trigger_dict.get(Trigger.UUID, "") or obj.uuid
        })
        obj.trigger_results_before = None
        if not util.get_args_flag("triggerless"):
            obj.trigger_results_before = await Trigger.run(obj.trigger_dict)

        return obj

    @abc.abstractmethod
    def prepare_create(self, request: dict):
        """
        Initialize a 'create' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request
        """

    def aprepare_create(self, request: dict):
        """
        Initialize a 'create' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request
        """
        raise NotImplementedError('aprepare_create not implemented')

    def prepare_edit(self, request: dict):
        """
        Initialize an 'edit' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request
        """
        raise NotImplementedError('Use POST with a matching UUID instead (PUT)')

    def aprepare_edit(self, request: dict):
        """
        Initialize an 'edit' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request
        """
        raise NotImplementedError('aprepare_edit not implemented')

    def prepare_terminate(self, request: dict):
        """
        Initialize a 'termination' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request

        """
        raise NotImplementedError

    def aprepare_terminate(self, request: dict):
        """
        Initialize a 'termination' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request

        """
        raise NotImplementedError('aprepare_terminate not implemented')

    def prepare_refresh(self, request: dict):
        """
        Initialize a 'refresh' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request

        """
        # Default it noop
        pass

    def aprepare_refresh(self, request: dict):
        """
        Initialize a 'refresh' request. Performs validation and all
        necessary processing

        :param request: A dict containing a request

        """
        # Default it noop
        pass

    def submit(self) -> str:
        """Submit the request to LoRa.

        :return: A string containing the result from submitting the
                 request to LoRa, typically a UUID.
        """
        self.trigger_dict.update({
            Trigger.RESULT: getattr(self, Trigger.RESULT, None),
            Trigger.EVENT_TYPE: EventType.ON_AFTER,
            Trigger.UUID: self.trigger_dict.get(Trigger.UUID, "") or self.uuid
        })
        self.trigger_results_after = None
        if not util.get_args_flag("triggerless"):
            self.trigger_results_after = in_separate_thread(
                async_to_sync(Trigger.run)
            )(
                self.trigger_dict
            )

        return getattr(self, Trigger.RESULT, None)

    async def asubmit(self) -> str:
        """Submit the request to LoRa.

        :return: A string containing the result from submitting the
                 request to LoRa, typically a UUID.
        """
        self.trigger_dict.update({
            Trigger.RESULT: getattr(self, Trigger.RESULT, None),
            Trigger.EVENT_TYPE: EventType.ON_AFTER,
            Trigger.UUID: self.trigger_dict.get(Trigger.UUID, "") or self.uuid
        })
        self.trigger_results_after = None
        if not util.get_args_flag("triggerless"):
            self.trigger_results_after = await Trigger.run(self.trigger_dict)

        return getattr(self, Trigger.RESULT, None)


class OrgFunkRequestHandler(RequestHandler):
    '''Abstract base class for automatically registering
    `organisationsfunktion`-based handlers.'''

    function_key = None
    '''
    When set, automatically register this class as a writing handler
    for `organisationsfunktion` objects with the corresponding
    ``funktionsnavn``.
    '''

    termination_field = mapping.ORG_FUNK_GYLDIGHED_FIELD
    '''The relation to change when terminating an employee tied to to an
    ``organisationsfunktion`` objects tied for `organisationsfunktion`
    objects with the corresponding ``funktionsnavn``.

    '''

    termination_value = {
        'gyldighed': 'Inaktiv',
    }
    '''On termination, the value to assign to the relation specified by
    :py:attr:`termination_field`.

    '''

    @classmethod
    def _register(cls):
        super()._register()

        # sanity checks
        assert cls.function_key is not None
        assert cls.role_type is not None
        assert cls.function_key not in HANDLERS_BY_FUNCTION_KEY

        HANDLERS_BY_FUNCTION_KEY[cls.function_key] = cls
        FUNCTION_KEYS[cls.role_type] = cls.function_key

    def prepare_terminate(self, request: dict):
        self.uuid = util.get_uuid(request)
        date = util.get_valid_to(request, required=True)

        original = async_to_sync(
            lora.Connector(effective_date=date).organisationfunktion.get
        )(self.uuid)

        if (
            original is None or
            util.is_reg_valid(original) and
            get_key_for_function(original) != self.function_key
        ):
            exceptions.ErrorCodes.E_NOT_FOUND(
                uuid=self.uuid,
                original=original,
            )

        self.payload = common.update_payload(
            date,
            util.POSITIVE_INFINITY,
            [(
                self.termination_field,
                self.termination_value,
            )],
            original,
            {
                'note': "Afsluttet",
            },
        )

        if self.trigger_dict.get(Trigger.EMPLOYEE_UUID, None) is None:
            self.trigger_dict[
                Trigger.EMPLOYEE_UUID
            ] = mapping.USER_FIELD.get_uuid(original)
        if self.trigger_dict.get(Trigger.ORG_UNIT_UUID, None) is None:
            self.trigger_dict[
                Trigger.ORG_UNIT_UUID
            ] = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

    def submit(self) -> str:
        c = lora.Connector()

        method = None
        if self.request_type == RequestType.CREATE:
            method = async_to_sync(c.organisationfunktion.create)
        else:
            method = async_to_sync(c.organisationfunktion.update)
        self.result = method(
            self.payload,
            self.uuid
        )
        return super().submit()


def get_key_for_function(obj: dict) -> str:
    '''Obtain the function key class corresponding to the given LoRA object'''

    # use unpacking to ensure that the set contains just one element
    (key,) = {
        attrs['funktionsnavn']
        for attrs in mapping.ORG_FUNK_EGENSKABER_FIELD(obj)
    }

    return key


def get_handler_for_function(obj: dict):
    '''Obtain the handler class corresponding to the given LoRA object'''

    return HANDLERS_BY_FUNCTION_KEY[get_key_for_function(obj)]


def get_handler_for_role_type(role_type: str):
    '''Obtain the handler class corresponding to given role_type'''

    try:
        return HANDLERS_BY_ROLE_TYPE[role_type]
    except LookupError:
        exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE(type=role_type)


def generate_requests(
    requests: typing.List[dict],
    request_type: RequestType
) -> typing.List[RequestHandler]:
    operations = {req.get('type') for req in requests}

    if not operations.issubset(HANDLERS_BY_ROLE_TYPE):
        exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE(
            types=sorted(operations - HANDLERS_BY_ROLE_TYPE.keys()),
        )

    requesthandlers = []
    for req in requests:
        requesthandler_klasse = HANDLERS_BY_ROLE_TYPE[req.get('type')]
        if req.get('type') in [
            'role', 'kle', 'itsystem', 'engagement_association', 'leave', 'orgunit'
        ] and request_type == RequestType.CREATE:
            requesthandlers.append(
                async_to_sync(
                    requesthandler_klasse.construct)(req, request_type)
            )
        elif req.get('type') in [
            'role'
        ] and request_type == RequestType.EDIT:
            requesthandlers.append(
                async_to_sync(
                    requesthandler_klasse.construct)(req, request_type)
            )
        else:
            requesthandlers.append(
                requesthandler_klasse(req, request_type)
            )
    return requesthandlers


def submit_requests(requests: typing.List[RequestHandler]) -> typing.List[str]:
    return [request.submit() for request in requests]
