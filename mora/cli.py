#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import sys
import unittest

import click

basedir = os.path.dirname(__file__)


def load_cli(app):
    @app.cli.command()
    @click.argument('target', required=False)
    def build(target=None):
        'Build the frontend application.'
        from subprocess import check_call, check_output

        base_dir = os.path.dirname(os.path.dirname(__file__))
        bin_dir = check_output(['npm', 'bin'], cwd=base_dir).decode().strip()

        check_call(['npm', 'install'], cwd=base_dir)
        check_call([os.path.join(bin_dir, 'grunt')] +
                   ([target] if target else []), cwd=base_dir)

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
                start_dir=os.path.join(basedir, '..', 'tests'),
                top_level_dir=os.path.join(basedir, '..'),
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

        runner = unittest.TextTestRunner(verbosity=verbosity, **kwargs)
        runner.run(suite)

    @app.cli.command()
    @click.option('--user', '-u',
                  help="account user name")
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
        import getpass

        import requests

        from . import tokens

        '''Request a SAML token'''
        def my_input(prompt):
            sys.stderr.write(prompt)
            return input()

        username = options['user'] or my_input('User: ')
        password = options['password'] or getpass.getpass('Password: ')

        if options['insecure']:
            from requests.packages import urllib3
            urllib3.disable_warnings()

        try:
            # this is where the magic happens
            token = tokens.get_token(
                username, password,
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
            import base64
            import ssl

            from lxml import etree

            for el in etree.fromstring(token).findall('.//{*}X509Certificate'):
                data = base64.standard_b64decode(el.text)

                sys.stdout.write(ssl.DER_cert_to_PEM_cert(data))

    @app.cli.command()
    @click.option('--user', '-u',
                  help="account user name")
    @click.option('--password', '-p',
                  help="account password")
    @click.option('--insecure', '-k', is_flag=True,
                  help="disable SSL/TLS security checks")
    @click.argument('path')
    def get(path, **options):
        '''Fetch objects.'''
        import getpass
        import json

        import requests

        from . import auth
        from . import lora
        from . import tokens

        '''Request a SAML token'''
        def my_input(prompt):
            sys.stderr.write(prompt)
            return input()

        if options['insecure']:
            from requests.packages import urllib3
            urllib3.disable_warnings()

        username = options['user'] or my_input('User: ')
        password = options['password'] or getpass.getpass('Password: ')

        lora.session.auth = auth.SAMLAuth(tokens.get_token(username, password))
        lora.session.verify = not options['insecure']

        for uuid in lora.fetch(path):
            print(json.dumps(lora.get(path.split('?')[0], uuid), indent=4))
