# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
import pprint
from time import sleep
from unittest.case import TestCase

from starlette.testclient import TestClient

from mora import app, conf_db, service, settings
from mora.async_util import async_to_sync
from mora.request_scoped.bulking import request_wide_bulk
from tests.util import _mox_testing_api, load_sample_structures


class _BaseTestCase(TestCase):
    """
    Base class for MO testcases w/o LoRA access.
    """

    maxDiff = None

    def setUp(self):
        super().setUp()
        app = self.create_app()
        self.client = TestClient(app)

    def create_app(self, overrides=None):
        # make sure the configured organisation is always reset
        # every before test
        service.org.ConfiguredOrganisation.valid = False
        app_ = app.create_app()

        return app_

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

        if r.headers.get('content-type') == 'application/json':
            actual = r.json()
        else:
            print(r.headers, r.content, r.raw)
            actual = r.text

        # actual = (
        #     json.loads(r.get_data(True))
        #     if r.mimetype == 'application/json'
        #     else r.get_data(True)
        # )

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
                ppa = pprint.pformat(actual)
                print(f'actual response:\n{ppa}')

                self.fail(message)

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

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

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

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

            # kwargs['method'] = 'POST'
            kwargs['data'] = json.dumps(kwargs.pop('json'), indent=2)
            kwargs['headers'] = {'Content-Type': 'application/json'}
            return self.client.post(path, **kwargs)

        return self.client.get(path, **kwargs)

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

    def assertSortedEqual(self, expected, actual, message=None):
        """Sort all inner-lists before comparison"""

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        return self.assertEqual(expected, actual, message)


class TestCase(_BaseTestCase):
    pass


class LoRATestCase(_BaseTestCase):
    '''Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    '''

    @async_to_sync
    async def load_sample_structures(self, minimal=False):
        sleep(1)
        await load_sample_structures(minimal)

    @classmethod
    def setUpClass(cls):
        _mox_testing_api("db-setup")
        request_wide_bulk._disable_caching()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        _mox_testing_api("db-teardown")
        super().tearDownClass()

    def setUp(self):
        _mox_testing_api("db-reset")
        super().setUp()


class ConfigTestCase(LoRATestCase):
    """Testcase with configuration database support."""

    def set_global_conf(self, conf):
        conf_db.set_configuration({'org_units': dict(conf)})

    @classmethod
    def setUpClass(cls):
        conf_db.config["configuration"]["database"]["name"] = "test_confdb"
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        conf_db._createdb(force=False)
        super().setUp()

    def tearDown(self):
        conf_db.drop_db()
        super().tearDown()
