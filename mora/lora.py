#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import generator_stop

import collections
import datetime
import itertools
import functools
import uuid

import requests
from flask import g

from . import auth
from . import exceptions
from . import settings
from . import util


ALL_RELATION_NAMES = {
    'adresse',
    'adresser',
    'afgiftsobjekt',
    'afleveringsarkiv',
    'aktivitetdokument',
    'aktivitetgrundlag',
    'aktivitetresultat',
    'aktivitetstype',
    'andetarkiv',
    'andrebehandlere',
    'andredokumenter',
    'andreklasser',
    'andresager',
    'ansatte',
    'ansvarlig',
    'ansvarligklasse',
    'arkiver',
    'begrundelse',
    'behandlingarkiv',
    'besvarelser',
    'bilag',
    'branche',
    'bruger',
    'brugerrolle',
    'brugertyper',
    'byggeri',
    'deltager',
    'deltagerklasse',
    'ejendomsskat',
    'ejer',
    'emne',
    'enhedstype',
    'erstatter',
    'facet',
    'facettilhoerer',
    'facilitet',
    'facilitetklasse',
    'foelsomhedklasse',
    'foelsomhedsklasse',
    'fordelttil',
    'fredning',
    'geoobjekt',
    'grundlagklasse',
    'handlingsklasse',
    'indsatsaktoer',
    'indsatsdokument',
    'indsatsklasse',
    'indsatskvalitet',
    'indsatsmodtager',
    'indsatssag',
    'indsatstype',
    # NB: also an attribute :(
    # 'interessefaellesskabstype',
    'journalpost',
    'kommentarer',
    'kontoklasse',
    'kopiparter',
    'lokale',
    'lovligekombinationer',
    'mapninger',
    'myndighed',
    'myndighedstype',
    'nyrevision',
    'objekt',
    'objektklasse',
    'opgaveklasse',
    'opgaver',
    'organisatoriskfunktionstype',
    'overordnet',
    'overordnetklasse',
    'oversag',
    'parter',
    'position',
    'praecedens',
    'primaerbehandler',
    'primaerklasse',
    'primaerpart',
    'produktionsenhed',
    'redaktoerer',
    'rekvirentklasse',
    'resultatklasse',
    'samtykke',
    'sekundaerpart',
    'sideordnede',
    'sikkerhedsklasse',
    'skatteenhed',
    'systemtyper',
    'tilfoejelser',
    'tilhoerer',
    'tilknyttedebrugere',
    'tilknyttedeenheder',
    'tilknyttedefunktioner',
    'tilknyttedeinteressefaellesskaber',
    'tilknyttedeitsystemer',
    'tilknyttedeorganisationer',
    'tilknyttedepersoner',
    'tilknyttedesager',
    'tilstandsaktoer',
    'tilstandsdokument',
    'tilstandskvalitet',
    'tilstandsobjekt',
    'tilstandstype',
    'tilstandsudstyr',
    'tilstandsvaerdi',
    'tilstandsvurdering',
    'udfoerer',
    'udfoererklasse',
    'udgangspunkter',
    'udlaanttil',
    'virksomhed',
    'virksomhedstype',
    'ydelsesklasse',
    'ydelsesmodtager',
}


class AuthorizedSession(requests.Session):

    def __init__(self, retries=0, max_retries=5, import_settings=settings):

        # Init Session
        super().__init__()

        # Set retry values
        self.retries = retries
        self.max_retries = max_retries

        # Set user agent header
        self.headers['User-Agent'] = 'MORA/0.1'

        # SSL signature verification
        self.verify = import_settings.CA_BUNDLE or True

        # Fetch token from context
        token = self.get_token_from_context()

    def get_token_from_context(self, context=g):
        """
        Retrieve user token from application context
        and set the authorization header for backend (lora) requests.

        ("http://flask.pocoo.org/docs/0.12/api/?highlight=g#flask.g")

        In "app.py":
            attach_user_token_to_context()

        is fetching the token from the authorization header
        and attaching the token value to the application context.

        :param context:     Application context
                            For more information,
                            head to the official flask documentation.
        """

        # User token
        token = context.user_token

        # TODO: Replace exception with proper exception type
        if not token:
            raise Exception(
                "No valid token found"
            )

        # Attach token to auth header
        self.headers['Authorization'] = token


def _check_response(r):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        try:
            d = r.json()
        except ValueError:
            raise exceptions.ValidationError(r.text)

        if r.status_code == 400 and d:
            raise exceptions.ValidationError(r.json()['message'])
        elif r.status_code in (401, 403) and d:
            raise exceptions.UnauthorizedError(r.json()['message'])
        else:
            raise

    return r


def get(path, uuid, **params):

    d = fetch(path, uuid=str(uuid), **params)

    if not d or not d[0]:
        return None

    registrations = d[0]['registreringer']

    assert len(d) == 1

    if params.keys() & {'registreretfra', 'registrerettil'}:
        return registrations
    else:
        assert len(registrations) == 1

        return registrations[0]


def fetch(path, **params):
    # Init session
    session = AuthorizedSession()
    r = session.get(settings.LORA_URL + path, params=params)
    _check_response(r)

    try:
        return r.json()['results'][0]
    except IndexError:
        return []


def create(path, obj, uuid=None):
    # Init session
    session = AuthorizedSession()

    if uuid:
        r = session.put('{}{}/{}'.format(settings.LORA_URL, path, uuid),
                        json=obj)
        _check_response(r)
        return uuid
    else:
        r = session.post(settings.LORA_URL + path, json=obj)
        _check_response(r)
        return r.json()['uuid']


def delete(path, uuid):
    # Init session
    session = AuthorizedSession()

    r = session.delete('{}{}/{}'.format(settings.LORA_URL, path, uuid))
    _check_response(r)


def update(path, obj):
    r = session.put(settings.LORA_URL + path, json=obj)
    _check_response(r)
    return r.json()['uuid']


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

        self.today = util.parsedatetime(
            defaults.pop('effective_date', None) or util.today(),
        )
        self.tomorrow = self.today + datetime.timedelta(days=1)

        if self.__validity == 'past':
            self.__daterange = (util.negative_infinity, self.today)
            defaults.update(
                virkningfra='-infinity',
                virkningtil=util.to_lora_time(self.today),
            )

        elif self.__validity == 'future':
            self.__daterange = (self.tomorrow, util.positive_infinity)

            defaults.update(
                virkningfra=util.to_lora_time(self.tomorrow),
                virkningtil='infinity',
            )

        elif self.__validity == 'present':
            if 'virkningfra' in defaults or 'virkningtil' in defaults:
                self.today = util.parsedatetime(defaults['virkningfra'])
                self.tomorrow = util.parsedatetime(defaults['virkningtil'])

            else:
                defaults.update(
                    virkningfra=util.to_lora_time(self.today),
                    virkningtil=util.to_lora_time(self.tomorrow),
                )

            self.__daterange = (self.today, self.tomorrow)

        else:
            raise exceptions.ValidationError(
                'invalid validity {!r}'.format(self.__validity),
            )

        self.__defaults = defaults

    @property
    def defaults(self):
        return self.__defaults

    @property
    def validity(self):
        return self.__validity

    def __is_range_relevant(self, start, end):
        if self.validity == 'present':
            return util.do_ranges_overlap(
                start, end,
                *self.__daterange,
            )

        else:
            return (
                util.do_ranges_overlap(start, end, *self.__daterange) and
                not util.do_ranges_overlap(start, end,
                                           self.today, self.tomorrow)
            )

    def get_date_chunks(self, dates):
        a, b = itertools.tee(sorted(dates))

        # drop the first item -- doing a raw next() fails in Python 3.7
        for x in itertools.islice(b, 1):
            pass

        yield from filter(
            lambda s: self.__is_range_relevant(*s),
            zip(a, b),
        )

    def __getattr__(self, attr):
        try:
            path = self.scope_map[attr]
        except KeyError:
            raise AttributeError(attr)

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

        # Init session
        self.session = AuthorizedSession()

    @property
    def base_path(self):
        return settings.LORA_URL + self.path

    def fetch(self, **params):
        r = self.session.get(self.base_path, params={
            **self.connector.defaults,
            **params,
        })

        _check_response(r)

        try:
            return r.json()['results'][0]
        except IndexError:
            return []

    __call__ = fetch

    def get_all(self, *, start=0, limit=1000, **params):
        params['maximalantalresultater'] = start + limit

        if 'uuid' in params:
            uuids = util.uniqueify(params['uuid'])
        else:
            uuids = self.fetch(**params)[start:start + limit]

        wantregs = params.keys() & {'registreretfra', 'registrerettil'}

        for chunk in util.splitlist(uuids, 20):
            for d in self.fetch(uuid=chunk):
                yield d['id'], (d['registreringer'] if wantregs
                                else d['registreringer'][0])

    def paged_get(self, func, *, start=0, limit=1000, **params):

        uuids = self.fetch(**params)

        return {
            'total': len(uuids),
            'offset': start,
            'items': [
                func(self.connector, obj_id, obj)
                for obj_id, obj in self.get_all(
                    start=start, limit=limit, **params)
            ],
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
            r = self.session.put('{}/{}'.format(self.base_path, uuid),
                            json=obj)
            _check_response(r)
            return uuid
        else:
            r = self.session.post(self.base_path, json=obj)
            _check_response(r)
            return r.json()['uuid']

    def delete(self, uuid):
        r = self.session.delete('{}/{}'.format(self.base_path, uuid))
        _check_response(r)

    def update(self, obj, uuid):
        r = self.session.put('{}/{}'.format(self.base_path, uuid), json=obj)
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

        chunks = set()

        everything = collections.defaultdict(tuple)

        for group in relevant:
            everything[group] += relevant[group]
        for group in also or {}:
            everything[group] += also[group]

        # extract all beginning and end timestamps for all effects
        for group, keys in relevant.items():
            if group not in reg:
                continue

            entries = reg[group]

            for key in keys:
                if key not in entries:
                    continue

                for entry in entries[key]:
                    chunks.update((
                        util.parsedatetime(entry['virkning']['from']),
                        util.parsedatetime(entry['virkning']['to']),
                    ))

        # sort them, and apply the filter, if given
        chunks = self.connector.get_date_chunks(chunks)

        def filter_list(entries, start, end):
            for entry in entries:
                entry_start = util.parsedatetime(entry['virkning']['from'])
                entry_end = util.parsedatetime(entry['virkning']['to'])

                if entry_start < end and entry_end > start:
                    yield entry

        # finally, extract chunks corresponding to each cut-off
        for start, end in chunks:
            effect = {
                group: {
                    key: list(filter_list(reg[group][key], start, end))
                    for key in everything[group]
                    if key in everything[group] and key in reg[group]
                }
                for group in everything
                if group in reg
            }

            if any(k for g in effect.values() for k in g.values()):
                yield start, end, effect


organisation = functools.partial(fetch, 'organisation/organisation')
organisation.get = functools.partial(get, 'organisation/organisation')
organisation.delete = functools.partial(delete, 'organisation/organisation')

organisationenhed = functools.partial(fetch, 'organisation/organisationenhed')
organisationenhed.get = \
    functools.partial(get, 'organisation/organisationenhed')
organisationenhed.delete = \
    functools.partial(delete, 'organisation/organisationenhed')

klasse = functools.partial(fetch, 'klassifikation/klasse')
klasse.get = functools.partial(get, 'klassifikation/klasse')
klasse.delete = functools.partial(delete, 'klassifikation/klasse')

# organisation = Connector('organisation/organisation')
# organisationenhed = Connector('organisation/organisationenhed')
# klasse = Connector('klassifikation/klasse')


# TODO: this function is used a lot, but should we put it elsewhere...
def get_org_unit(unitid: str) -> dict:
    """
    Get an org unit for in the time span from -infinity to +infinity
    :param unitid: the UUID of the org unit
    :return: the org unit
    """
    return organisationenhed.get(
        uuid=unitid,
        virkningfra='-infinity',
        virkningtil='infinity'
    )
