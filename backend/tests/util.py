#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


from collections import Counter
import contextlib
import json
import os
import pkgutil
import pprint
import re
import sys
import threading
from unittest.mock import patch

import flask
import flask_testing
import jinja2
import requests_mock
import time
import werkzeug.serving

from oio_rest.utils import test_support
from mora import triggers, app, lora, settings, service


TESTS_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(TESTS_DIR)
FIXTURE_DIR = os.path.join(TESTS_DIR, 'fixtures')
MOCKING_DIR = os.path.join(TESTS_DIR, 'mocking')

TOP_DIR = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(TOP_DIR, 'frontend')
DOCS_DIR = os.path.join(TOP_DIR, 'docs')

BUILD_DIR = os.path.join(BASE_DIR, 'build')
REPORTS_DIR = os.path.join(BUILD_DIR, 'reports')

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=FIXTURE_DIR,
    ),
)


def is_frontend_built():
    return os.path.isfile(
        os.path.join(app.distdir, 'index.html'),
    )


def jsonfile_to_dict(path):
    """
    Reads JSON from resources folder and converts to Python dictionary
    :param path: path to json resource
    :return: dictionary corresponding to the resource JSON
    """
    try:
        with open(os.path.join(BASE_DIR, path)) as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError('failed to decode ' + path)


def get_fixture(fixture_name, **kwargs):
    if not kwargs:
        return jsonfile_to_dict(os.path.join(FIXTURE_DIR, fixture_name))
    else:
        return json.loads(
            jinja_env.get_template(fixture_name).render(**kwargs),
        )


def get_mock_data(mock_name):
    return jsonfile_to_dict(os.path.join(MOCKING_DIR, mock_name))


def get_mock_text(mock_name, mode='r'):
    with open(os.path.join(MOCKING_DIR, mock_name), mode) as fp:
        return fp.read()


def load_fixture(path, fixture_name, uuid=None, **kwargs):
    '''Load a fixture, i.e. a JSON file with the 'fixtures' directory,
    into LoRA at the given path & UUID.

    '''
    print('creating', path, uuid, file=sys.stderr)
    r = lora.create(path, get_fixture(fixture_name, **kwargs), uuid)
    return r


def add_resetting_endpoint(app, fixture_name):
    @app.route('/reset-db')
    def reset_db():
        app.logger.warning('RESETTING DATABASE!!!')

        # TODO reset db

        return '', 200

    return app


def load_sample_structures(*, verbose=False, minimal=False, check=False,
                           delete=False):
    '''Inject our test data into LoRA.

    '''
    orgid = '456362c4-0ee4-4e5e-a72c-751239745e62'

    if delete:
        c = lora.Connector()

        print('deleting', c.organisation.path, orgid, file=sys.stderr)
        c.organisation.delete(orgid)

        for scope, rel in (
            (c.facet, 'ansvarlig'),
            (c.klasse, 'ansvarlig'),
            (c.organisationenhed, 'tilhoerer'),
            (c.organisationfunktion, 'tilknyttedeorganisationer'),
            (c.bruger, 'tilhoerer'),
            (c.itsystem, 'tilhoerer'),
        ):
            for objid in scope.fetch(**{rel: orgid}):
                print('deleting', scope.path, objid, file=sys.stderr)
                scope.delete(objid)

    fixtures = [(
        'organisation/organisation',
        'create_organisation_AU.json',
        orgid,
    )]

    units = {
        'root': '2874e1dc-85e6-4269-823a-e1125484dfd3',
    }

    classes = {
        'afdeling': '32547559-cfc1-4d97-94c6-70b192eff825',
    }

    facets = {
        'enhedstype': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280',
        'adressetype': 'e337bab4-635f-49ce-aa31-b44047a43aa1',
        'tilknytningstype': 'ef71fe9c-7901-48e2-86d8-84116e210202',
    }

    # TODO: add classifications, etc.

    functions = {
        'engagement': 'd000591f-8705-4324-897a-075e3623f37b',
        'tilknytning': 'c2153d5d-4a2b-492d-a18c-c498f7bb6221',
        'rolle': '1b20d0b9-96a0-42a6-b196-293bb86e62e8',
        'orlov': 'b807628c-030c-4f5f-a438-de41c1f26ba5',
        'leder': '05609702-977f-4869-9fb4-50ad74c6999a',
        'itsystem_user': 'aaa8c495-d7d4-4af1-b33a-f4cb27b82c66',
        'itsystem_unit': 'cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276',
        'tilknyttetenhed_hist': 'daa77a4d-6500-483d-b099-2c2eb7fa7a76',
        'tilknyttetenhed_hum': '5c68402c-2a8d-4776-9237-16349fc72648',
    }

    users = {
        'andersand': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
        'fedtmule': '6ee24785-ee9a-4502-81c2-7697009c9053',
    }

    itsystems = {
        'ad': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
        'lora': '0872fb72-926d-4c5c-a063-ff800b8ee697',
    }

    if not minimal:
        units.update({
            'hum': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            'samf': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            'fil': '85715fc7-925d-401b-822d-467eb4b163b6',
            'hist': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
            'frem': '04c78fc2-72d2-4d02-b55f-807af19eac48',
        })

        classes.update({
            'fakultet': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
            'institut': 'ca76a441-6226-404f-88a9-31e02e420e52',
            'email': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            'telefon': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
            'adresse': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            'ean': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
            'medlem': '62ec821f-4179-4758-bfdf-134529d186e9',
        })

        functions.update({
            'email_andersand': 'fba61e38-b553-47cc-94bf-8c7c3c2a6887',
            'email_fedtmule': '64ea02e2-8469-4c54-a523-3d46729e86a7',
            'adresse_fedtmule': 'cd6008bc-1ad2-4272-bc1c-d349ef733f52',
            'adresse_root': '414044e0-fe5f-4f82-be20-1e107ad50e80',
            'adresse_hum': 'e1a9cede-8c9b-4367-b628-113834361871',
            'tlf_hum': '55848eca-4e9e-4f30-954b-78d55eec0473',
            'ean_hum': 'a0fe7d43-1e0d-4232-a220-87098024b34d',
        })

    for facetkey, facetid in facets.items():
        fixtures.append((
            'klassifikation/facet',
            'create_facet_{}.json'.format(facetkey),
            facetid,
        ))

    for classkey, classid in classes.items():
        fixtures.append((
            'klassifikation/klasse',
            'create_klasse_{}.json'.format(classkey),
            classid,
        ))

    for unitkey, unitid in units.items():
        fixtures.append((
            'organisation/organisationenhed',
            'create_organisationenhed_{}.json'.format(unitkey),
            unitid,
        ))

    for funckey, funcid in functions.items():
        fixtures.append((
            'organisation/organisationfunktion',
            'create_organisationfunktion_{}.json'.format(funckey),
            funcid,
        ))

    for userkey, userid in users.items():
        fixtures.append((
            'organisation/bruger',
            'create_bruger_{}.json'.format(userkey),
            userid,
        ))

    for itsystemkey, itsystemid in itsystems.items():
        fixtures.append((
            'organisation/itsystem',
            'create_itsystem_{}.json'.format(itsystemkey),
            itsystemid,
        ))

    for path, fixture_name, uuid in fixtures:
        if check:
            if lora.get(path, uuid):
                raise Exception('{} already exists at {}!'.format(
                    uuid, path,
                ))
        else:
            load_fixture(path, fixture_name, uuid)


@contextlib.contextmanager
def override_settings(**overrides):
    stack = contextlib.ExitStack()
    with stack:
        for k, v in overrides.items():
            stack.enter_context(patch('mora.settings.{}'.format(k), v))

        yield


def override_lora_url(lora_url='http://mox/'):
    return patch('mora.settings.LORA_URL', lora_url)


@contextlib.contextmanager
def override_config(**overrides):
    originals = {}

    for k, v in overrides.items():
        originals[k] = flask.current_app.config[k]
        flask.current_app.config[k] = v

    yield

    flask.current_app.config.update(overrides)


class mock(requests_mock.Mocker):
    '''Decorator for running a function under requests_mock, with the
    given mocking fixture loaded, and optionally overriding the LORA
    URL to a fixed location.

    '''

    def __init__(self, names=None, allow_mox=False, **kwargs):
        super().__init__(**kwargs)

        self.__names = names
        self.__allow_mox = allow_mox
        self.__kwargs = kwargs

        if names:
            if not isinstance(names, (list, tuple)):
                names = [names]

            # inject the fixture; note that complete_qs is
            # important: without it, a URL need only match *some*
            # of the query parameters passed, and that's quite
            # obnoxious if requests only differ by them
            for name in names:
                for url, value in get_mock_data(name).items():
                    self.get(url, json=value, complete_qs=True)

        if not allow_mox:
            self.__overrider = override_lora_url()
        else:
            self.__overrider = None
            self.register_uri(
                requests_mock.ANY,
                re.compile('^{}/.*'.format(settings.LORA_URL.rstrip('/'))),
                real_http=True,
            )

    def copy(self):
        """Returns an exact copy of current mock
        """
        return mock(self.__names, self.__allow_mox, **self.__kwargs)

    def start(self):
        if self.__overrider:
            self.__overrider.__enter__()

        super().start()

    def stop(self):
        super().stop()

        if self.__overrider:
            self.__overrider.__exit__(None, None, None)


class TestCaseMixin(object):

    '''Base class for MO testcases w/o LoRA access.
    '''

    maxDiff = None

    def setUp(self):
        self.amqp_counter = Counter()

        def amqp_publish_message_mock(service, object_type, action, __, ___):
            topic = '{}.{}.{}'.format(service, object_type, action)
            self.amqp_counter[topic] += 1
        triggers.internal.amqp_trigger.publish_message = (
            amqp_publish_message_mock
        )
        super().setUp()

    def create_app(self, overrides=None):
        os.makedirs(BUILD_DIR, exist_ok=True)

        # make sure the configured organisation is always reset
        # every before test
        service.org.ConfiguredOrganisation.valid = False

        return app.create_app({
            'ENV': 'testing',
            'DUMMY_MODE': True,
            'DEBUG': False,
            'TESTING': True,
            'LIVESERVER_PORT': 0,
            'PRESERVE_CONTEXT_ON_EXCEPTION': False,
            'SECRET_KEY': 'secret',
            **(overrides or {})
        })

    @property
    def lora_url(self):
        return settings.LORA_URL

    def assertRequest(self, path, status_code=None, message=None, *,
                      drop_keys=(), amqp_topics=(), **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        :return: The result of the request, as a string or object, if
                 JSON.

        '''
        r = self.request(path, **kwargs)

        actual = (
            json.loads(r.get_data(True))
            if r.mimetype == 'application/json'
            else r.get_data(True)
        )

        if status_code is None:
            if message is None:
                message = 'status of {!r} was {}, not 2xx'.format(
                    path,
                    r.status_code,
                )

            if not 200 <= r.status_code < 300:
                pprint.pprint(actual)

                self.fail(message)

        else:
            if message is None:
                message = 'status of {!r} was {}, not {}'.format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                pprint.pprint(actual)

                self.fail(message)

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

        # example:
        # {
        #     'employee.create.it': 3,
        #     'organisation.edit.association': 1,
        # }
        amqp_recieved = Counter(amqp_topics)
        self.assertEqual(self.amqp_counter, amqp_recieved)

        return actual

    def assertRequestResponse(self, path, expected, message=None,
                              amqp_topics=(), **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        '''

        actual = self.assertRequest(path, message=message,
                                    amqp_topics=amqp_topics, **kwargs)

        if actual != expected:
            pprint.pprint(actual)

        self.assertEqual(expected, actual, message)

    def assertRequestFails(self, path, code, message=None, **kwargs):
        '''Issue a request and assert that it fails with the given status.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        '''

        self.assertRequest(path, message=message, status_code=code,
                           **kwargs)

    def request(self, path, **kwargs):
        if 'json' in kwargs:
            # "In the face of ambiguity, refuse the temptation to guess."
            # ...so check that the arguments we override don't exist
            assert kwargs.keys().isdisjoint({'method', 'data', 'headers'})

            kwargs['method'] = 'POST'
            kwargs['data'] = json.dumps(kwargs.pop('json'), indent=2)
            kwargs['headers'] = {'Content-Type': 'application/json'}

        return self.client.open(path, **kwargs)

    @staticmethod
    def __sort_inner_lists(obj):
        """Sort all inner lists and tuples by their JSON string value,
        recursively. This is quite stupid and slow, but works!

        This is purely to help comparison tests, as we don't care
        about the list ordering

        """
        if isinstance(obj, dict):
            return {
                k: TestCase.__sort_inner_lists(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, tuple)):
            return sorted(
                map(TestCase.__sort_inner_lists, obj),
                key=(lambda p: json.dumps(p, sort_keys=True)),
            )
        else:
            return obj

    def assertRegistrationsEqual(self, expected, actual, message=None):

        # drop lora-generated timestamps & users
        for k in 'fratidspunkt', 'tiltidspunkt', 'brugerref':
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        if actual != expected:
            pprint.pprint(actual)

        # Sort all inner lists and compare
        return self.assertEqual(expected, actual, message)

    def assertRegistrationsNotEqual(self, expected, actual, message=None):
        # drop lora-generated timestamps & users
        for k in 'fratidspunkt', 'tiltidspunkt', 'brugerref':
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        # Sort all inner lists and compare
        return self.assertNotEqual(expected, actual, message)


class LoRATestCaseMixin(test_support.TestCaseMixin, TestCaseMixin):
    '''Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    '''

    db_structure_extensions = json.loads(
        pkgutil.get_data('mora', 'db_extensions.json').decode(),
    )

    def load_sample_structures(self, **kwargs):
        load_sample_structures(**kwargs)

    def add_resetting_endpoint(self):
        '''Add an endpoint for resetting the database'''

        add_resetting_endpoint(self.app)

    def setUp(self):
        lora_server = werkzeug.serving.make_server(
            'localhost', 0, self.get_lora_app(),
        )
        (_, self.lora_port) = lora_server.socket.getsockname()

        # apply patches, then start the server -- so they're active
        # while it's running
        p = override_lora_url('http://localhost:{}/'.format(self.lora_port))
        p.start()
        self.addCleanup(p.stop)

        threading.Thread(
            target=lora_server.serve_forever,
            args=(),
        ).start()

        # likewise, stop it, and *then* pop the patches
        self.addCleanup(lora_server.shutdown)

        super().setUp()


class TestCase(TestCaseMixin, flask_testing.TestCase):
    pass


class LoRATestCase(LoRATestCaseMixin, flask_testing.TestCase):
    pass


class LiveLoRATestCase(LoRATestCaseMixin, flask_testing.LiveServerTestCase):
    #
    # The two methods below force the WSGI server to run in a thread
    # rather than a process. This enables easy coverage gathering as
    # output buffering.
    #
    def _spawn_live_server(self):
        self._server = werkzeug.serving.make_server(
            'localhost', self._port_value.value, self.app,
        )

        self._port_value.value = self._server.socket.getsockname()[1]

        self._thread = threading.Thread(
            target=self._server.serve_forever,
            args=(),
        )
        self._thread.start()

        # Copied from flask_testing

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        timeout = self.app.config.get('LIVESERVER_TIMEOUT', 5)
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time)
            if elapsed_time > timeout:
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % timeout
                )

            if self._can_ping_server():
                break

    def _terminate_live_server(self):
        self._server.shutdown()
        self._thread.join()
