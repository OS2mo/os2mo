# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from __future__ import generator_stop

import typing
import uuid

import requests

import flask_saml_sso
from functools import partial
from itertools import starmap
from more_itertools import chunked

import lora_utils
from . import exceptions
from . import settings
from . import util

session = requests.Session()
session.verify = settings.CA_BUNDLE or True
session.auth = flask_saml_sso.SAMLAuth()
session.headers = {
    'User-Agent': 'MORA/0.1',
}


def _check_response(r):
    if not r.ok:
        try:
            cause = r.json()
            msg = cause['message']
        except (ValueError, KeyError):
            cause = None
            msg = r.text

        if r.status_code == 400:
            exceptions.ErrorCodes.E_INVALID_INPUT(message=msg, cause=cause)
        elif r.status_code == 401:
            exceptions.ErrorCodes.E_UNAUTHORIZED(message=msg, cause=cause)
        elif r.status_code == 403:
            exceptions.ErrorCodes.E_FORBIDDEN(message=msg, cause=cause)
        else:
            exceptions.ErrorCodes.E_UNKNOWN(message=msg, cause=cause)

    return r


class Connector:

    scope_map = dict(
        organisation='organisation/organisation',
        organisationenhed='organisation/organisationenhed',
        organisationfunktion='organisation/organisationfunktion',
        bruger='organisation/bruger',
        itsystem='organisation/itsystem',
        klasse='klassifikation/klasse',
        facet='klassifikation/facet',
        klassifikation='klassifikation/klassifikation',
    )

    def __init__(self, **defaults):
        self.__validity = defaults.pop('validity', None) or 'present'

        self.now = util.parsedatetime(
            defaults.pop('effective_date', None) or util.now(),
        )

        if self.__validity == 'past':
            self.start = util.NEGATIVE_INFINITY
            self.end = self.now

        elif self.__validity == 'future':
            self.start = self.now
            self.end = util.POSITIVE_INFINITY

        elif self.__validity == 'present':
            # we should probably use 'virkningstid' but that means we
            # have to override each and every single invocation of the
            # accessors later on
            if 'virkningfra' in defaults:
                self.start = self.now = util.parsedatetime(
                    defaults.pop('virkningfra'),
                )
            else:
                self.start = self.now

            if 'virkningtil' in defaults:
                self.end = util.parsedatetime(defaults.pop('virkningtil'))
            else:
                self.end = self.start + util.MINIMAL_INTERVAL

        else:
            exceptions.ErrorCodes.V_INVALID_VALIDITY(validity=self.__validity)

        defaults.update(
            virkningfra=util.to_lora_time(self.start),
            virkningtil=util.to_lora_time(self.end),
            konsolider=True,
        )

        self.__defaults = defaults

    @property
    def defaults(self):
        return self.__defaults

    @property
    def validity(self):
        return self.__validity

    def is_range_relevant(self, start, end, effect):
        if self.validity == 'present':
            return util.do_ranges_overlap(self.start, self.end, start, end)
        else:
            return start > self.start and end <= self.end

    def __getattr__(self, attr):
        try:
            path = self.scope_map[attr]
        except KeyError:
            raise AttributeError(
                attr + " should be one of: " + str(list(self.scope_map.keys()))
            )

        scope = Scope(self, path)
        setattr(self, attr, scope)

        return scope

    def is_effect_relevant(self, effect):
        return self.__is_range_relevant(util.parsedatetime(effect['from']),
                                        util.parsedatetime(effect['to']))


class Scope:
    def __init__(self, connector, path):
        self.connector = connector
        self.path = path
        self.max_uuids = self._calculate_max_uuids()

    @property
    def base_path(self):
        return settings.LORA_URL + self.path

    def _calculate_max_uuids(self):
        """Calculate the maximum number of UUIDs which can be send at once.

        Used by :code:`get_all_by_uuid` to minimize the number of roundtrips,
        while simultaneously ensuring that requests are valid.

        The method works by starting of with the maximum valid-length of a HTTP
        Request-Line. Then gradually reserving characters, as needed for Method,
        URL and non-uuid URL parameters. Finally the left-over length is divded
        to maximize the number of UUIDs.
        """
        available_length = settings.MAX_REQUEST_LENGTH
        available_length -= len('GET ')
        available_length -= len(self.base_path)

        for k, v in self.connector.defaults.items():
            # Note & may instead be ? for the first parameter.
            available_length -= len("&") + len(k) + len('=') + len(str(v))

        # At the point we know that available_length characters are left for
        # UUIDs, each uuid consumes 36 charactesrs and a header.
        per_length = len('&uuid=') + 36
        max_uuids = int(available_length / per_length)
        return max_uuids

    def fetch(self, **params):
        r = session.get(self.base_path, params={
            **self.connector.defaults,
            **params,
        })

        _check_response(r)

        try:
            return r.json()['results'][0]
        except IndexError:
            return []

    __call__ = fetch

    def get_all(self, **params):
        """Perform a search on given params and return the result.

        As we perform a search in LoRa, using 'uuid' as a parameter is not supported,
        as LoRa will raise in error.

        Currently we hardcode the use of 'list' to return items from the search,
        so supplying 'list' as a parameter is not supported.

        Returns an iterator of tuples (obj_id, obj) of all matches.
        """
        ass_msg = "'{}' is not a supported parameter for 'get_all'{}."
        assert "list" not in params, ass_msg.format("list", ", implicitly set")
        assert "uuid" not in params, ass_msg.format("uuid", ", use 'get_all_by_uuid'")
        assert "start" not in params, ass_msg.format("start", ", use 'paged_get'")
        assert "limit" not in params, ass_msg.format("limit", ", use 'paged_get'")

        wantregs = not params.keys().isdisjoint(
            {'registreretfra', 'registrerettil'}
        )

        for d in self.fetch(**dict(params), list=1):
            yield d['id'], (d['registreringer'] if wantregs
                            else d['registreringer'][0])

    def get_all_by_uuid(self, uuids: typing.List, elements_per_chunk=None):
        """Get a list of objects by their UUIDs.

        Returns an iterator of tuples (obj_id, obj) of all matches.
        """
        # If elements_per_chunk is None, use self.max_uuids as default
        elements_per_chunk = elements_per_chunk or self.max_uuids
        # Whatever the value of elements_per_chunk, self.max_uuids is the max
        elements_per_chunk = min(elements_per_chunk, self.max_uuids)

        for chunk in chunked(uuids, elements_per_chunk):
            for d in self.fetch(uuid=chunk):
                yield d['id'], (d['registreringer'][0])

    def paged_get(self, func, *,
                  start=0, limit=settings.DEFAULT_PAGE_SIZE,
                  uuid_filters=None,
                  **params):
        """Perform a search on given params, filter and return the result.

        :code:`func` is a function from (lora-connector, obj_id, obj) to
        :code:`item-type`.

        :code:`uuid_filters` is a list of functions from uuid to bool, where
        the uuid will be kept assuming the returned bool is truthy.

        Returns paged dict with 3 keys: 'total', 'offset' and 'items', where:
            'total' is the total number of matches found.
            'offset' is the offset into 'total' (for pagination).
            'items' is a list of :code:`item-type` items.
        """
        uuid_filters = uuid_filters or []
        # Fetch all uuids matching search params and filter with uuid_filters
        uuids = self.fetch(**params)
        for uuid_filter in uuid_filters:
            uuids = filter(uuid_filter, uuids)
        # Sort to ensure consistent order, as LoRa does not seem to do that
        uuids = sorted(list(uuids))
        total = len(uuids)
        # Offset by slicing off the start
        uuids = uuids[start:]
        # Limit by slicing off the end
        if limit > 0:
            uuids = uuids[:limit]
        # Lookup objects by uuid, and build objects using func
        obj_iter = self.get_all_by_uuid(uuids)
        obj_iter = starmap(partial(func, self.connector), obj_iter)
        return {
            'total': total,
            'offset': start,
            'items': list(obj_iter)
        }

    def get(self, uuid, **params):
        d = self.fetch(uuid=str(uuid), **params)

        if not d or not d[0]:
            return None

        registrations = d[0]['registreringer']

        assert len(d) == 1

        if params.keys() & {'registreretfra', 'registrerettil'}:
            return registrations
        else:
            assert len(registrations) == 1

            return registrations[0]

    def create(self, obj, uuid=None):
        if uuid:
            r = session.put('{}/{}'.format(self.base_path, uuid),
                            json=obj)
        else:
            r = session.post(self.base_path, json=obj)

        _check_response(r)
        return r.json()['uuid']

    def delete(self, uuid):
        r = session.delete('{}/{}'.format(self.base_path, uuid))
        _check_response(r)

    def update(self, obj, uuid):
        r = session.request(
            'PATCH',
            '{}/{}'.format(self.base_path, uuid),
            json=obj,
        )
        _check_response(r)
        return r.json()['uuid']

    def get_effects(self, obj, relevant, also=None, **params):
        reg = (
            self.get(obj, **params)
            if isinstance(obj, (str, uuid.UUID))
            else obj
        )

        if not reg:
            return

        effects = list(lora_utils.get_effects(reg, relevant, also))

        return filter(
            lambda a: self.connector.is_range_relevant(*a),
            effects,
        )


def get_version():
    r = session.get(settings.LORA_URL + "version")
    try:
        return r.json()["lora_version"]
    except ValueError:
        return "Could not find lora version: %s" % r.text
