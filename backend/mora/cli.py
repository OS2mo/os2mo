#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Management utility for MORA.

Please note that each command below also takes a ``--help`` argument
which describes its arguments and options.

The three most important commands are ``build``, ``run`` and
``full-run``:

Use ``build`` for building the frontend sources. Then, use ``run`` to
serve the MORA webapp with reloading. This is particularly useful for
backend development.

Use ``full-run`` to run the entire stack, with webapp served with
reloading. The database is a one-off database, starting with the
same state as our TestCafé tests. This is primarily useful for
frontend development.

In addition, we have ``docs`` for building the documentation.

'''

import contextlib
import doctest
import json
import os
import pkgutil
import random
import subprocess
import sys
import threading
import traceback
import unittest

import click
import flask
import werkzeug.serving

from . import settings

basedir = os.path.dirname(__file__)
backenddir = os.path.dirname(basedir)
topdir = os.path.dirname(backenddir)
docsdir = os.path.join(topdir, 'docs')
frontenddir = os.path.join(topdir, 'frontend')


group = flask.cli.FlaskGroup(help=__doc__, context_settings={
    'help_option_names': ['-h', '--help'],
})


class Exit(click.ClickException):
    '''A click exception for simply exiting the script'''

    def __init__(self, exit_code: int=1):
        self.exit_code = exit_code

    def show(self):
        pass


def get_yarn_cmd(cmd):
    with open(os.path.join(frontenddir, 'package.json')) as fp:
        info = json.load(fp)

    args = info['scripts'][cmd].split()

    if args[0] not in ('node', 'npm', 'yarn'):
        args[0] = os.path.join(frontenddir, 'node_modules', '.bin', args[0])

    return args


@group.command()
@click.argument('target', required=False)
def build(target=None):
    'Build the frontend application.'

    subprocess.check_call(['yarn'], cwd=frontenddir)
    subprocess.check_call(get_yarn_cmd('build'), cwd=frontenddir)

    if target:
        subprocess.check_call(
            ['yarn', 'run'] + ([target] if target else []),
            cwd=frontenddir)


@group.command()
@click.option('-b', '--open-browser', is_flag=True)
@click.argument('destdir', type=click.Path(), required=False)
def docs(open_browser, destdir):
    '''Build the documentation'''
    import webbrowser

    import sphinx.cmdline

    vuedoc_cmd = [
        os.path.join(frontenddir, 'node_modules', '.bin', 'vuedoc.md'),
        '--output', os.path.join(docsdir, 'vuedoc'),
    ] + [
        os.path.join(dirpath, file_name)
        for dirpath, dirs, file_names in
        os.walk(os.path.join(frontenddir, 'src'))
        for file_name in file_names
        if file_name.endswith('.vue')
    ]

    subprocess.check_call(vuedoc_cmd)

    if destdir:
        destdir = click.format_filename(destdir)
    else:
        destdir = os.path.join(topdir, 'docs', 'out', 'html')

    sphinx.cmdline.main(['-b', 'html', docsdir, destdir])

    if open_browser:
        webbrowser.get('default').open(click.format_filename(destdir))


@group.command()
@click.option('--verbose', '-v', count=True,
              help='Show more output.')
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.option('--failfast/--no-failfast', '-f',
              default=False, show_default=True,
              help='Stop at first failure.')
@click.option('--buffer/--no-buffer', '-b/-B',
              default=True, show_default=True,
              help='Toggle buffering of standard output during runs.')
@click.option('--minimox-dir', help='Location for a checkout of the '
              'minimox branch of LoRA.')
@click.option('--browser', help='Specify browser for Selenium tests, '
              'e.g. "Safari", "Firefox" or "Chrome".')
@click.option('--list', '-l', 'do_list', is_flag=True,
              help='List all available tests',)
@click.option('--xml-report', type=click.Path(),
              help='Write XML report to the given location',)
@click.option('--randomise', '--randomize', 'randomise', is_flag=True,
              help='Randomise execution order',)
@click.option('--keyword', '-k', 'keywords', multiple=True,
              help='Only run or list tests matching the given keyword',)
@click.argument('tests', nargs=-1)
def test(tests, quiet, verbose, minimox_dir, browser, do_list,
         keywords, xml_report, **kwargs):
    '''Test the application.'''
    sys.path.insert(0, backenddir)

    verbosity = 0 if quiet else verbose + 1

    if minimox_dir:
        os.environ['MINIMOX_DIR'] = minimox_dir

    if browser:
        os.environ['BROWSER'] = browser

    loader = unittest.TestLoader()

    # ensure that we can load the tests, whatever the $PWD
    sys.path.insert(0, backenddir)

    if tests:
        def as_module(tn):
            if os.path.isfile(tn) and tn.endswith('.py'):
                return '.'.join(
                    os.path.split(
                        os.path.splitext(
                            os.path.relpath(tn, backenddir)
                        )[0]
                    )
                )
            else:
                return tn

        suite = loader.loadTestsFromNames(map(as_module, tests))

    else:
        suite = loader.discover(
            start_dir=os.path.join(backenddir, 'tests'),
            top_level_dir=os.path.join(backenddir),
        )

        for module in sys.modules.values():
            module_file = getattr(module, '__file__', None)

            if module_file and module_file.startswith(basedir):
                suite.addTests(doctest.DocTestSuite(
                    module,
                    optionflags=(
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
                    ),
                ))

    def expand_suite(suite):
        for member in suite:
            if isinstance(member, unittest.TestSuite):
                yield from expand_suite(member)
            else:
                yield member

    tests = list(expand_suite(suite))

    if keywords:
        tests = [
            case
            for k in keywords
            for case in tests
            if k.lower() in str(case).lower()
        ]

    if kwargs.pop('randomise'):
        random.SystemRandom().shuffle(tests)

    suite = unittest.TestSuite(tests)

    if do_list:
        for case in suite:
            if verbose:
                print(case)
            elif not quiet:
                print(case.id())

        return

    if xml_report:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(verbosity=verbosity,
                                         output=xml_report, **kwargs)

    else:
        runner = unittest.TextTestRunner(verbosity=verbosity, **kwargs)

    try:
        result = runner.run(suite)

    except Exception:
        if verbosity > 1:
            traceback.print_exc()
        raise

    if not result.wasSuccessful():
        raise Exit()


@contextlib.contextmanager
def make_dummy_instance():
    from unittest import mock

    import psycopg2

    from oio_rest import app as lora_app
    from oio_rest.utils import test_support
    from oio_rest import settings as lora_settings

    from mora import app

    # ensure that we can import the tests module, regardless of $PWD
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    sys.path.pop(0)

    def make_server(app, startport=5000):
        '''create a server at the first available port after startport'''
        last_exc = None

        for port in range(startport, 65536):
            try:
                return (
                    werkzeug.serving.make_server(
                        'localhost', port, app,
                        threaded=True,
                    ),
                    port,
                )
            except OSError as exc:
                last_exc = exc

        if last_exc is not None:
            raise last_exc

    exts = json.loads(
        pkgutil.get_data('mora', 'db_extensions.json').decode(),
    )

    with test_support.psql() as psql, contextlib.ExitStack() as stack:

        def doublepatch(k, v, *, create=False):
            stack.enter_context(
                mock.patch("oio_rest.settings." + k, v, create=create)
            )

            stack.enter_context(
                mock.patch("mora.settings." + k, v, create=create)
            )

        for k, v in {
            "oio_rest.settings.DB_HOST": psql.dsn()["host"],
            "oio_rest.settings.DB_PORT": psql.dsn()["port"],
            "oio_rest.settings.LOG_AMQP_SERVER": None,
            "oio_rest.db.pool": psycopg2.pool.PersistentConnectionPool(
                0, 100, **psql.dsn(database=lora_settings.DATABASE)
            ),
        }.items():
            stack.enter_context(mock.patch(k, v, create=True))

        stack.enter_context(test_support.extend_db_struct(exts))

        mora_server, mora_port = make_server(app.create_app(), 5000)
        lora_server, lora_port = make_server(lora_app.create_app(), 6000)

        stack.enter_context(
            mock.patch(
                "mora.settings.LORA_URL",
                "http://localhost:{}/".format(lora_port),
            )
        )

        with stack:
            test_support._initdb()

            yield psql, lora_server, mora_server


@group.command()
@click.option('--fixture', type=click.Choice(['empty', 'minimal', 'simple',
                                              'small', 'normal', 'large']),
              default='normal',
              help='Choose the initial dataset.')
def full_run(fixture):
    '''Command for running a one-off server for frontend development.

    This server consists of a the following:

        1. An embedded PostgreSQL server.

        2. An embedded LoRA/OIO REST WSGI server, loaded with either
           the somewhat expansive *“Hjørring”* fixture, or with
           ``--simple``, the *“Aarhus Universitet”* dummy fixture.

        3. An embedded MO REST WSGI server.

        4. A node process serving the frontend code in development
           mode using ``vue-cli-service``.

    Please note that neither OIO REST nor the MO API are served with
    reloading; as such, any changes to the Python code requires a
    restart.

    The command prints out how to access each server at load. The
    ports are normally allocated as follows:

        1. PostgreSQL uses a random available port.

        2. OIO REST uses the first available port starting from port
           6000.

        3. MO uses the first available port starting
           from port 5000.

        4. ``vue-cli-service`` uses the first available port starting
           from port 8080.

    Normally, this server is run using the ``flask.sh`` script. If
    something goes wrong, such as a missing or outdated dependency,
    simply delete the Python virtual environment and re-run the
    command::

       $ pwd
       /path/to/os2mo/backend
       $ rm -rf ./venv
       $ ./flask.sh full-run
       Creating virtual environment!
       [...]

    '''

    from oio_rest import settings as lora_settings

    from tests import util as test_util

    with make_dummy_instance() as (psql, lora_server, mora_server):
        print(' * PostgreSQL running at {}'.format(psql.url(
            database=lora_settings.DATABASE,
        )))
        print(' * LoRA running at {}'.format(settings.LORA_URL))
        print(' * Backend running at http://localhost:{}/'
              .format(mora_server.port))

        test_util.load_sql_fixture(fixture + '.sql')
        test_util.add_resetting_endpoint(mora_server.app, fixture + '.sql')

        threading.Thread(
            target=lora_server.serve_forever,
            args=(),
            daemon=True,
        ).start()

        threading.Thread(
            target=mora_server.serve_forever,
            args=(),
            daemon=True,
        ).start()

        subprocess.check_call(
            get_yarn_cmd('dev'),
            cwd=frontenddir,
            env={
                **os.environ,
                'BASE_URL':
                'http://localhost:{}'.format(mora_server.port),
            },
        )


@group.command()
@click.argument('fixture-name', metavar='NAME', default='normal')
@click.option('-o', 'target', type=click.File(mode='w',
                                              lazy=True, atomic=True))
def update_fixture(fixture_name, target):
    '''Update a given fixture'''

    with make_dummy_instance() as (psql, lora_server, mora_server):
        from oio_rest import settings as lora_settings
        from tests import util as test_util

        threading.Thread(
            target=lora_server.serve_forever,
            args=(),
            daemon=True,
        ).start()

        if fixture_name == 'simple':
            test_util.load_sample_structures()

        elif fixture_name == 'minimal':
            test_util.load_sample_structures(minimal=True)

        else:
            from os2mo_data_import import ImportHelper
            from fixture_generator import populate_mo
            from fixture_generator import dummy_data_creator

            try:
                org_size = getattr(dummy_data_creator.Size,
                                   fixture_name.title())
            except AttributeError:
                raise click.exceptions.BadArgumentUsage(
                    'Unexpected fixture name {!r}'.format(fixture_name),
                )

            threading.Thread(
                target=mora_server.serve_forever,
                args=(),
                daemon=True,
            ).start()

            importer = ImportHelper(
                create_defaults=True,
                mox_base=settings.LORA_URL,
                mora_base='http://localhost:{}/'.format(mora_server.port),
                system_name="Artificial import",
                end_marker="STOP",
                store_integration_data=True,
            )

            populate_mo.CreateDummyOrg(
                importer,
                '0860',
                'Hjørring Kommune',
                scale=1,
                org_size=org_size,
                extra_root=True,
            )

            importer.import_all()

            mora_server.shutdown()

        lora_server.shutdown()

        if target is None:
            target = open(os.path.join(test_util.FIXTURE_DIR,
                                       fixture_name.lower() + '.sql'),
                          mode='w')

        with target:
            subprocess.check_call(
                [
                    'pg_dump',
                    '--data-only',
                    '--dbname', lora_settings.DATABASE,
                    '--host', lora_settings.DB_HOST,
                    '--port', str(lora_settings.DB_PORT),
                    '--username', lora_settings.DB_USER,
                ],
                stdout=target,
            )


if __name__ == '__main__':
    group(prog_name=os.getenv('FLASK_PROG_NAME', sys.argv[0]))
