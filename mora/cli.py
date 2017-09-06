#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import base64
import functools
import json
import os
import ssl
import sys
import traceback
import unittest
import warnings

import click
import requests
import urllib3

from . import auth
from . import lora
from . import tokens
from . import util
from .converters import importing

basedir = os.path.dirname(__file__)
topdir = os.path.dirname(basedir)


def requires_auth(func):
    @click.option('--user', '-u',
                  help="account user name")
    @click.option('--password', '-p',
                  help="account password")
    @click.option('--insecure', '-k', is_flag=True,
                  help="disable SSL/TLS security checks")
    def wrapper(*args, **options):
        if options.pop('insecure'):
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
            )

            lora.session.auth = auth.SAMLAuth(assertion)

            return func(*args, **options)
        except urllib3.exceptions.HTTPWarning as e:
            print(e)
            print('or use -k/--insecure to suppress this warning')
            raise click.Abort()

        except PermissionError as e:
            print('Authentication failed:', e)
            raise click.Abort()

    return functools.update_wrapper(wrapper, func)


def load_cli(app):
    @app.cli.command()
    @click.option('--outdir', '-o',
                  default=os.path.join(topdir, 'docs', 'out'),
                  help='Output directory.')
    @click.option('--verbose', '-v', count=True,
                  help='Show more output.')
    @click.argument('args', nargs=-1)
    def sphinx(outdir, verbose, args):
        '''Build documentation'''
        import sphinx.cmdline

        if args:
            args = list(args)
        else:
            args = [
                '-b', 'html',
                topdir,
                outdir,
            ]

        args += ['-v'] * verbose

        r = sphinx.cmdline.main(['sphinx-build'] + args)
        if r:
            sys.exit(r)

    @app.cli.command()
    @click.argument('target', required=False)
    def build(target=None):
        'Build the frontend application.'
        from subprocess import check_call

        check_call(['npm', 'install'], cwd=topdir)
        check_call(['npm', 'run', 'grunt'] +
                   ([target] if target else []), cwd=topdir)

    @app.cli.command()
    @click.argument('args', nargs=-1)
    def python(args):
        os.execv(sys.executable, (sys.executable,) + args)

    @app.cli.command(with_appcontext=False)
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
    @click.option('--list', '-l', is_flag=True,
                  help='List all available tests')
    @click.argument('tests', nargs=-1)
    def test(tests, quiet, verbose, minimox_dir, browser, list, **kwargs):
        verbosity = 0 if quiet else verbose + 1

        if minimox_dir:
            os.environ['MINIMOX_DIR'] = minimox_dir

        if browser:
            os.environ['BROWSER'] = browser

        loader = unittest.TestLoader()

        if tests:
            suite = loader.loadTestsFromNames(tests)
        else:
            suite = loader.discover(
                start_dir=os.path.join(topdir, 'tests'),
                top_level_dir=os.path.join(topdir),
            )

        if list:
            def expand_suite(suite):
                for member in suite:
                    if isinstance(member, unittest.TestSuite):
                        yield from expand_suite(member)
                    else:
                        yield member

            for case in expand_suite(suite):
                if verbose:
                    print(case)
                elif not quiet:
                    print(case.id())

            return

        try:
            runner = unittest.TextTestRunner(verbosity=verbosity, **kwargs)
            runner.run(suite)

        except Exception:
            if verbosity > 1:
                traceback.print_exc()
            raise

    @app.cli.command()
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
    def auth(**options):
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

    @app.cli.command()
    @click.argument('path')
    @requires_auth
    def get(path):
        for objuuid in lora.fetch(path):
            print(objuuid)
            json.dump(lora.get(path.split('?')[0], objuuid),
                      sys.stdout, indent=4)
            sys.stdout.write('\n')

    @app.cli.command()
    @click.argument('path')
    @click.argument('input', type=click.File('rb'), default='-')
    @requires_auth
    def update(path, input):
        lora.put(path, json.load(input))

    @app.cli.command('import')
    @click.argument('spreadsheet', type=click.File('rb'))
    @click.argument('url', required=False)
    @click.option('--verbose', '-v', count=True,
                  help='Show more output.')
    @click.option('--check', '-c', is_flag=True,
                  help=('check if import would overwrite any existing '
                        'objects'))
    @requires_auth
    def import_(url, spreadsheet, verbose, check):
        '''
        Import an Excel spreadsheet into LoRa
        '''

        # apparently, you cannot call tzlocal after importing gevent/eventlets
        util.now()

        import grequests

        sheetlines = importing.convert(spreadsheet)

        if not url:
            for method, path, obj in sheetlines:
                print(method, path,
                      json.dumps(obj, indent=2))
            return

        requests = (
            grequests.request(
                # check means that we always get GET anything
                method if not check else 'GET',
                url + path, session=lora.session,
                json=obj,
            )
            for method, path, obj in sheetlines
        )

        def fail(r, exc):
            if verbose:
                print(r.url)
            print(*exc.args)

        for r in grequests.imap(requests, size=6, exception_handler=fail):
            if verbose:
                print(r.url)

            if check:
                if r.ok:
                    print('EXISTS:', r.request.path_url)
                elif r.status_code == 404:
                    print('CREATE:', r.request.path_url)

            elif not r.ok:
                try:
                    print(r.status_code, r.json())
                except ValueError:
                    print(r.status_code, r.text)
            r.raise_for_status()

    @app.cli.command('load-fixtures')
    @click.option('--quiet', '-q', is_flag=True,
                  help='Suppress all output.')
    @click.option('--minimal', is_flag=True,
                  help='Just import the root unit.')
    @click.option('--check', '-c', is_flag=True,
                  help=('check if import would overwrite any existing '
                        'objects'))
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
