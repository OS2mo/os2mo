#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools

import requests

from . import auth
from . import settings
from . import util

session = requests.Session()
session.verify = settings.CA_BUNDLE or True
session.auth = auth.SAMLAuth()


def _check_response(r):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400 and r.json():
            raise ValueError(r.json()['message'])
        elif r.status_code in (401, 403) and r.json():
            raise PermissionError(r.json()['message'])
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
    r = session.get(settings.LORA_URL + path, params=params)
    _check_response(r)

    try:
        return r.json()['results'][0]
    except IndexError:
        return []


def create(path, obj, uuid=None):
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
        klasse='klassifikation/klasse',
    )

    def __init__(self, **overrides):
        self.__validity = overrides.pop('validity', None) or 'present'

        self.today = util.parsedatetime(
            overrides.pop('effective_date', None) or util.today(),
        )
        self.tomorrow = self.today + datetime.timedelta(days=1)

        if self.__validity == 'past':
            overrides.update(
                virkningfra='-infinity',
                virkningtil=util.to_lora_time(self.today),
            )

        elif self.__validity == 'future':
            overrides.update(
                virkningfra=util.to_lora_time(self.tomorrow),
                virkningtil='infinity',
            )

        elif self.__validity == 'present':
            if 'virkningfra' in overrides or 'virkningtil' in overrides:
                self.today = util.parsedatetime(overrides['virkningfra'])
                self.tomorrow = util.parsedatetime(overrides['virkningtil'])

            else:
                overrides.update(
                    virkningfra=util.to_lora_time(self.today),
                    virkningtil=util.to_lora_time(self.tomorrow),
                )

        else:
            raise ValueError('invalid validity {!r}'.format(self.__validity))

        self.__overrides = overrides

    @property
    def overrides(self):
        return self.__overrides

    @property
    def validity(self):
        return self.__validity

    def get_date_chunks(self, dates):
        if self.__validity == 'present':
            dates = sorted(dates)

            for start, end in zip(dates, dates[1:]):
                if self.tomorrow >= start and self.today <= end:
                    yield start, end

            return

        elif self.__validity == 'past':
            dates = sorted(filter(lambda d: d <= self.today, dates))

        elif self.__validity == 'future':
            dates = sorted(filter(lambda d: d > self.tomorrow, dates))

        yield from zip(dates, dates[1:])

    def __getattr__(self, attr):
        try:
            path = self.scope_map[attr]
        except KeyError:
            raise AttributeError(attr)

        return Scope(self, path)

    def override(self, overrides):
        new_overrides = self.__overrides.copy()
        new_overrides.update(overrides)

        return Connector(new_overrides)


class Scope:
    def __init__(self, connector, path):
        self.connector = connector
        self.path = path

    @property
    def base_path(self):
        return settings.LORA_URL + self.path

    def fetch(self, **params):
        params.update(self.connector.overrides)

        r = session.get(self.base_path, params=params)
        _check_response(r)

        try:
            return r.json()['results'][0]
        except IndexError:
            return []

    __call__ = fetch

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
            _check_response(r)
            return uuid
        else:
            r = session.post(self.base_path, json=obj)
            _check_response(r)
            return r.json()['uuid']

    def delete(self, uuid):
        r = session.delete('{}/{}'.format(self.base_path, uuid))
        _check_response(r)

    def update(self, obj):
        r = session.put(self.base_path, json=obj)
        _check_response(r)
        return r.json()['uuid']

    def get_effects(self, uuid: str, relevant, **params):
        reg = self.get(uuid, **params)

        chunks = set()

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
                    for key in relevant[group]
                    if key in relevant[group]
                }
                for group in relevant
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
