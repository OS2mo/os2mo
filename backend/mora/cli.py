#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Management utility for MORA.

'''


import base64
import doctest
import functools
import importlib
import json
import os
import posixpath
import random
import signal
import ssl
import subprocess
import sys
import threading
import traceback
import unittest
import warnings

import click
import flask
import pyexcel
import requests
import urllib3
import werkzeug.serving

from . import exceptions
from . import lora
from . import settings
from . import util
from .auth import base, tokens

basedir = os.path.dirname(__file__)
backenddir = os.path.dirname(basedir)
topdir = os.path.dirname(backenddir)
frontenddir = os.path.join(topdir, 'frontend')


class AppGroup(flask.cli.FlaskGroup):
    '''Subclass of default app Flask group that adds -h to all commands.'''
    __context_settings = {
        'help_option_names': ['-h', '--help']
    }

    def command(self, *args, **kwargs):
        ''
        kwargs.setdefault('context_settings', self.__context_settings)

        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        ''
        kwargs.setdefault('context_settings', self.__context_settings)

        return super().group(*args, **kwargs)


def create_app(self):
    from . import app

    return app.app


group = AppGroup(
    'mora', help=__doc__,
    create_app=create_app,
)


class Exit(click.ClickException):
    def __init__(self, exit_code: int=1):
        self.exit_code = exit_code

    def show(self):
        pass


def requires_auth(func):
    @click.option('--user', '-u',
                  help="account user name")
    @click.option('--password', '-p',
                  help="account password")
    @click.option('--insecure', '-k', is_flag=True,
                  help="disable SSL/TLS security checks")
    def wrapper(*args, **options):
        insecure = options.pop('insecure')

        if insecure:
            warnings.simplefilter('ignore', urllib3.exceptions.HTTPWarning)

            lora.session.verify = False
        else:
            warnings.simplefilter('error', urllib3.exceptions.HTTPWarning)

        if options['user'] and not options['password']:
            options['password'] = click.prompt(
                'Enter password for {}'.format(
                    options['user'],
                ),
                hide_input=True,
                err=True,
            )

        try:
            assertion = tokens.get_token(
                options.pop('user'),
                options.pop('password'),
                insecure=insecure,
            )

            lora.session.auth = base.SAMLAuth(assertion)

            return func(*args, **options)
        except urllib3.exceptions.HTTPWarning as e:
            if flask.current_app.debug:
                traceback.print_exc()
            else:
                print(e)
            print('or use -k/--insecure to suppress this warning')
            raise click.Abort()

        except exceptions.HTTPException as exc:
            click.secho('Authentication failed! {}'.format(exc),
                        fg='red', bold=True)
            click.echo(json.dumps(exc.body, indent=2))
            raise click.Abort()

    return functools.update_wrapper(wrapper, func)


@group.command()
@click.argument('target', required=False)
def build(target=None):
    'Build the frontend application.'

    subprocess.check_call(['yarn'], cwd=frontenddir)
    subprocess.check_call(['yarn', 'build'], cwd=frontenddir)

    if target:
        subprocess.check_call(
            ['yarn', 'run'] + ([target] if target else []),
            cwd=frontenddir)


@group.command()
def develop():
    'Run for development.'

    with subprocess.Popen(['yarn', 'start'],
                          close_fds=True,
                          cwd=frontenddir) as proc:
        try:
            flask.current_app.run()
        finally:
            proc.send_signal(signal.SIGINT)
            proc.wait()


@group.command()
@click.argument('args', nargs=-1)
def python(args):
    os.execv(sys.executable, (sys.executable,) + args)


@group.command(with_appcontext=False)
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
@flask.cli.with_appcontext
def test(tests, quiet, verbose, minimox_dir, browser, do_list,
         keywords, xml_report, **kwargs):
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
                suite.addTests(doctest.DocTestSuite(module))

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
            if k in str(case)
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


@group.command('auth')
@click.option('--user', '-u',
              help="account user name",
              prompt='Enter user name')
@click.option('--password', '-p',
              help="account password")
@click.option('--raw', '-r', is_flag=True,
              help="don't pack and wrap the token")
@click.option('--verbose', '-v', is_flag=True,
              help="pretty-print the token")
@click.option('--insecure', '-k', is_flag=True,
              help="disable SSL/TLS security checks")
@click.option('--cert-only', '-c', is_flag=True,
              help="output embedded certificates in PEM form")
def auth_(**options):
    if options['insecure']:
        warnings.simplefilter('ignore', urllib3.exceptions.HTTPWarning)
    else:
        warnings.simplefilter('error', urllib3.exceptions.HTTPWarning)

    if options['user'] and not options['password']:
        options['password'] = click.prompt(
            'Enter password for {}'.format(
                options['user'],
            ),
            hide_input=True,
            err=True,
        )

    try:
        # this is where the magic happens
        token = tokens.get_token(
            options['user'], options['password'],
            raw=options['raw'] or options['cert_only'],
            verbose=options['verbose'],
            insecure=options['insecure'],
        )
    except requests.exceptions.SSLError as e:
        msg = ('SSL request failed; you probably need to install the '
               'appropriate certificate authority, or use the correct '
               'host name.')
        print(msg, file=sys.stderr)
        print('error:', e, file=sys.stderr)

        raise click.Abort

    if not options['cert_only']:
        sys.stdout.write(token.decode())

    else:
        from lxml import etree

        for el in etree.fromstring(token).findall('.//{*}X509Certificate'):
            data = base64.standard_b64decode(el.text)

            sys.stdout.write(ssl.DER_cert_to_PEM_cert(data))


@group.command()
@click.argument('paths', nargs=-1)
@requires_auth
def get(paths):
    for path in paths:
        click.secho(path, bold=True)

        try:
            for obj in lora.fetch(path) or [None]:
                if isinstance(obj, str):
                    click.echo(obj)
                    obj = lora.get(path.split('?')[0], obj)

                json.dump(obj, sys.stdout, indent=4)
                sys.stdout.write('\n')

        except exceptions.HTTPException as exc:
            click.secho('ERROR: {}'.format(exc), fg='red', bold=True)
            json.dump(exc.body, sys.stdout, indent=2)


@group.command()
@click.argument('path')
@click.argument('input', type=click.File('rb'), default='-')
@requires_auth
def update(path, input):
    lora.put(path, json.load(input))


@group.command('import')
@click.argument('name')
@click.argument('sheets', nargs=-1, type=click.Path())
@click.option('--target', '-t', default=settings.LORA_URL)
@click.option('--output', '-o', type=click.File('w'))
@click.option('--compact', '-c', is_flag=True)
@click.option('--dry-run', '-n', is_flag=True,
              help=("don't actually change anything"))
@click.option('--verbose', '-v', count=True,
              help='Show more output.')
@click.option('--jobs', '-j', default=1, type=int,
              help='Amount of parallel requests.')
@click.option('--failfast', '-f', is_flag=True,
              help='Stop at first error.')
@click.option('--include', '-I', multiple=True,
              help='include only the given types.')
@click.option('--check', '-c', is_flag=True,
              help=('check if import would overwrite any existing '
                    'objects'))
@click.option('--exact', '-e', is_flag=True,
              help="don't calculate missing values")
@click.option('--delimiter', '-d', default=None, type=str)
@click.option('--charset', '-c', default=None, type=str,
              help='input file encoding')
@requires_auth
def import_file(name, **kwargs):
    '''
    Import an Excel spreadsheet into LoRa
    '''

    if '.' not in name:
        module_name = 'mora.importing.' + name.replace('-', '_')

    try:
        module = importlib.import_module(module_name)
    except ImportError:
        if flask.current_app.debug or kwargs['verbose']:
            traceback.print_exc()

        raise click.BadOptionUsage('{} is not a known importer'.format(name))

    if not hasattr(module, 'run'):
        raise click.BadOptionUsage('{} is not a valid importer'.format(name))

    module.run(**kwargs)


@group.command('sheet-convert', with_appcontext=False)
@click.option('--sheet', '-s',
              help='only convert the given sheet')
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.argument('source', type=click.Path())
@click.argument('destination', type=click.Path())
def sheetconvert(sheet, quiet, source, destination):
    '''Convert a spreadsheet to another format.

    Supports CSV, ODS, XLSX and possibly more.
    '''

    if not quiet:
        print('{} -> {}'.format(source, destination))

    if sheet:
        pyexcel.save_as(
            file_name=source,
            dest_file_name=destination,
            sheet_name=sheet,
        )
    else:
        pyexcel.save_book_as(
            file_name=source,
            dest_file_name=destination,
        )


@group.command('load-fixtures')
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.option('--minimal', is_flag=True,
              help='Just import the root unit.')
@click.option('--check', '-c', is_flag=True,
              help=('check if import would overwrite any existing '
                    'objects'))
@click.option('--delete', '-d', is_flag=True,
              help=('empty and delete organisation first'))
@requires_auth
def load_fixtures(**kwargs):
    '''
    Import the sample fixtures into LoRA.
    '''

    from tests import util

    util.load_sample_structures(
        verbose=not kwargs.pop('quiet'),
        **kwargs,
    )


@group.command('run-with-db')
@click.option('hostname', '--host', '-h', default='localhost',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('use_reloader', '--reload/--no-reload', default=None,
              help='Enable or disable the reloader.  By default the reloader '
              'is active if debug is enabled.')
@click.option('use_debugger', '--debugger/--no-debugger', default=None,
              help='Enable or disable the debugger.  By default the debugger '
              'is active if debug is enabled.')
@click.option('use_reloader', '--eager-loading/--lazy-loader', default=None,
              help='Enable or disable eager loading.  By default eager '
              'loading is enabled if the reloader is disabled.')
@click.option('threaded', '--with-threads/--without-threads', default=True,
              help='Enable or disable multithreading.')
def run_with_db(**kwargs):
    from unittest import mock

    import psycopg2

    from oio_rest import app as lora_app
    from oio_rest.utils import test_support
    import settings as lora_settings

    from mora import app
    from mora.importing import spreadsheets

    with \
            test_support.psql() as psql, \
            mock.patch('settings.LOG_AMQP_SERVER', None), \
            mock.patch('settings.DB_HOST', psql.dsn()['host'], create=True), \
            mock.patch('settings.DB_PORT', psql.dsn()['port'], create=True):
        test_support._initdb()

        lora_server = werkzeug.serving.make_server(
            'localhost', 0, lora_app.app,
            threaded=kwargs['threaded'],
        )

        lora_port = lora_server.socket.getsockname()[1]

        lora_thread = threading.Thread(
            target=lora_server.serve_forever,
            args=(),
            daemon=True,
        )

        lora_thread.start()

        with \
                mock.patch('oio_rest.db.pool',
                           psycopg2.pool.PersistentConnectionPool(
                               1, 100,
                               database=lora_settings.DATABASE,
                               user=psql.dsn()['user'],
                               password=psql.dsn().get('password'),
                               host=psql.dsn()['host'],
                               port=psql.dsn()['port'],
                           )), \
                mock.patch('mora.settings.LORA_URL',
                           'http://localhost:{}/'.format(lora_port)):
            print(' * LoRA running at {}'.format(settings.LORA_URL))

            spreadsheets.run(
                target=settings.LORA_URL.rstrip('/'),
                sheets=[
                    os.path.join(
                        backenddir,
                        'tests/fixtures/importing/BALLERUP.csv',
                    ),
                ],
                dry_run=False,
                verbose=False,
                jobs=1,
                failfast=False,
                include=None,
                check=False,
                exact=False,
            )

            werkzeug.serving.run_simple(application=app.app, **kwargs)


@group.command()
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.option('--dry-run', '-n', is_flag=True,
              help=("don't actually change anything"))
@click.option('--yes', '-y', is_flag=True,
              help=("don't prompt for confirmation before making changes"))
@requires_auth
def fixroots(**kwargs):
    '''
    Import the sample fixtures into LoRA.
    '''

    # apparently, you cannot call tzlocal after importing gevent/eventlets
    util.now()

    import grequests

    unitids = lora.organisationenhed(bvn='%')
    requests = (
        grequests.get(
            posixpath.join(settings.LORA_URL,
                           'organisation', 'organisationenhed'),
            session=lora.session,
            params={
                'uuid': unitids[i:i + 10],
            },
        )
        for i in range(0, len(unitids), 20)
    )

    for r in grequests.imap(requests, size=6):
        for entry in r.json()['results'][0]:
            unitid = entry['id']
            unit = entry['registreringer'][-1]

            if unit['relationer'].get('overordnet'):
                continue

            print(unitid)

            tilhoerer = unit['relationer']['tilhoerer'][0]

            unit['note'] = \
                'Relation til organisation som overordnet tilføjet'
            unit['relationer']['overordnet'] = [
                {
                    'uuid': tilhoerer['uuid'],
                    'virkning': tilhoerer['virkning'].copy(),
                },
            ]

            print(json.dumps(unit, indent=2))

            if not kwargs['dry_run'] and (
                    kwargs['yes'] or
                    click.prompt('Perform update', prompt_suffix='? ',
                                 err=True).lower() in ('y', 'yes')
            ):
                lora.update(
                    posixpath.join('organisation', 'organisationenhed',
                                   unitid),
                    unit,
                )


if __name__ == '__main__':
    group(prog_name=os.environ.get('MORA_PROG_NAME'))
