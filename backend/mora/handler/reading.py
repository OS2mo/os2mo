# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import abc

import json
from asyncio import create_task, gather
from typing import Any, Dict, List, Tuple

import flask

from .. import util, exceptions
from .. import mapping

READING_HANDLERS = {}


def register(object_type):
    def decorator(cls):
        READING_HANDLERS[object_type] = cls
        return cls

    return decorator


def get_handler_for_type(object_type) -> 'ReadingHandler':
    try:
        return READING_HANDLERS[object_type]
    except LookupError:
        exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE(type=object_type)


class ReadingHandler:

    @classmethod
    @abc.abstractmethod
    async def get(cls, c, search_fields):
        """
        Read a list of objects based on the given search parameters

        :param c: A LoRa connector
        :param search_fields: A dict containing search parameters
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def get_from_type(cls, c, type, obj_uuid):
        """
        Read a list of objects related to a certain object

        :param c: A LoRa connector
        :param type: Either 'e' or 'ou' depending on if related to an
            employee or orgunit
        :param obj_uuid: The UUID of the related employee/orgunit
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def get_effects(cls, c, obj, **params):
        """
        Chunk a LoRa object up into effects

        :param c: A LoRa connector
        :param obj: An object to be chunked
        :param params: Additional parameters to be sent along to a LoRa
            chunking function
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def get_mo_object_from_effect(cls, effect, start, end, obj_id):
        """
        Convert an effect to a MO object

        :param effect: An effect to be convertd
        :param start: The start date for the effect
        :param end: The end date for the effect
        :param obj_id: The UUID of the object in LoRa the effect originates
            from
        """
        pass

    @classmethod
    async def async_get_mo_object_from_effect(cls, c, function_id,
                                              function_obj) -> List[Any]:
        """
        just a wrapper that makes calls in parallel. Not encapsulating / motivated by
        business logic
        :param c: A LoRa connector
        :param function_id: UUID from object_tuple
        :param function_id: object from object_tuple
        @return: List of whatever this returns get_mo_object_from_effect
        """
        return await gather(*[create_task(
            cls.get_mo_object_from_effect(effect, start, end, function_id))
            for start, end, effect in (await cls.get_effects(c, function_obj))
            if util.is_reg_valid(effect)])

    @classmethod
    async def get_obj_effects(cls, c, object_tuples):
        """
        Convert a list of LoRa objects into a list of MO objects

        :param c: A LoRa connector
        :param object_tuples: An iterable of (UUID, object) tuples
        """
        object_tuples = list(object_tuples)

        # flatten a bunch of nested tasks
        return [x for sublist in
                await gather(
                    *[create_task(cls.async_get_mo_object_from_effect(c,
                                                                      function_id,
                                                                      function_obj))
                      for function_id, function_obj in object_tuples])
                for x in sublist]


class OrgFunkReadingHandler(ReadingHandler):
    function_key = None

    SEARCH_FIELDS = {
        'e': 'tilknyttedebrugere',
        'ou': 'tilknyttedeenheder'
    }

    @classmethod
    async def get(cls, c, search_fields):
        object_tuples = await cls.get_lora_object(c, search_fields)
        return await cls.get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c, type, objid):

        search_fields = {
            cls.SEARCH_FIELDS[type]: objid
        }

        return await cls.get(c, search_fields)

    @classmethod
    def function_key_filter(cls, object_tuple: Tuple[str, Dict[Any, Any]]) -> bool:
        """

        :param object_tuple: UUID, object
        :return: whether function key mathces class
        """
        _, obj = object_tuple

        field = mapping.ORG_FUNK_EGENSKABER_FIELD(obj)

        if not field:
            return False

        return field[0]['funktionsnavn'] == cls.function_key

    @classmethod
    async def get_lora_object(cls, c, search_fields):
        object_tuples = await c.organisationfunktion.get_all(
            **search_fields,
        )

        object_tuples = list(object_tuples)
        if object_tuples:
            object_tuples = list(filter(cls.function_key_filter, object_tuples))

        return object_tuples

    @classmethod
    async def get_effects(cls, c, obj, **params):
        relevant = {
            'attributter': (
                'organisationfunktionegenskaber',
                'organisationfunktionudvidelser',
            ),
            'relationer': (
                'opgaver',
                'adresser',
                'organisatoriskfunktionstype',
                'tilknyttedeenheder',
                'tilknyttedeklasser',
                'tilknyttedebrugere',
                'tilknyttedefunktioner',
                'tilknyttedeitsystemer',
                'primær',
            ),
            'tilstande': (
                'organisationfunktiongyldighed',
            ),
        }
        also = {
            'relationer': (
                'tilhoerer',
                'tilknyttedeorganisationer',
            ),
        }

        return await c.organisationfunktion.get_effects(
            obj,
            relevant,
            also,
            **params
        )

    @classmethod
    async def get_mo_object_from_effect(cls, effect, start, end, funcid):
        properties = mapping.ORG_FUNK_EGENSKABER_FIELD(effect)[0]
        user_key = properties['brugervendtnoegle']

        r = {
            mapping.UUID: funcid,
            mapping.USER_KEY: user_key,
            mapping.VALIDITY: util.get_validity_object(start, end),
        }

        if properties.get('integrationsdata') is not None:
            try:
                r[mapping.INTEGRATION_DATA] = json.loads(
                    properties['integrationsdata'],
                )
            except json.JSONDecodeError:
                flask.current_app.logger.warning(
                    'invalid integration data for function %s!',
                    funcid,
                )
                r[mapping.INTEGRATION_DATA] = None

        return r
