# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import abc

import json

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
    def get(cls, c, search_fields):
        """
        Read a list of objects based on the given search parameters

        :param c: A LoRa connector
        :param search_fields: A dict containing search parameters
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_from_type(cls, c, type, obj_uuid):
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
    def get_effects(cls, c, obj, **params):
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
    def get_mo_object_from_effect(cls, effect, start, end, obj_id):
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
    def get_obj_effects(cls, c, object_tuples):
        """
        Convert a list of LoRa objects into a list of MO objects

        :param c: A LoRa connector
        :param object_tuples: A list of (UUID, object) tuples
        """
        return [
            cls.get_mo_object_from_effect(effect, start, end, function_id)
            for function_id, function_obj in object_tuples
            for start, end, effect in cls.get_effects(c, function_obj)
            if util.is_reg_valid(effect)
        ]


class OrgFunkReadingHandler(ReadingHandler):
    function_key = None

    SEARCH_FIELDS = {
        'e': 'tilknyttedebrugere',
        'ou': 'tilknyttedeenheder'
    }

    @classmethod
    def get(cls, c, search_fields):
        object_tuples = cls.get_lora_object(c, search_fields)
        return cls.get_obj_effects(c, object_tuples)

    @classmethod
    def get_from_type(cls, c, type, objid):

        search_fields = {
            cls.SEARCH_FIELDS[type]: objid
        }

        return cls.get(c, search_fields)

    @classmethod
    def get_lora_object(cls, c, search_fields):
        object_tuples = c.organisationfunktion.get_all(
            funktionsnavn=cls.function_key,
            **search_fields,
        )
        return object_tuples

    @classmethod
    def get_obj_effects(cls, c, object_tuples):
        return [
            cls.get_mo_object_from_effect(effect, start, end, function_id)
            for function_id, function_obj in object_tuples
            for start, end, effect in cls.get_effects(c, function_obj)
            if util.is_reg_valid(effect)
        ]

    @classmethod
    def get_effects(cls, c, obj, **params):
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

        return c.organisationfunktion.get_effects(
            obj,
            relevant,
            also,
            **params
        )

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
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
