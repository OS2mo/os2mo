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
import functools
import importlib
import json
import ssl
import sys
import traceback
import warnings

import click
import flask
import pyexcel
import requests
import urllib3

from .. import exceptions
from .. import lora
from .. import settings
from ..auth import base as auth_base, tokens as auth_tokens

from . import base


@base.cli.group('lora')
def group():
    '''Subcommands for interacting directly with LoRA.'''


def requires_auth(func):
    @click.option('--user', '-u',
                  help="account user name")
    @click.option('--password', '-p',
                  help="account password")
    @click.option('--insecure', '-k', is_flag=True,
                  help="disable SSL/TLS security checks")
    @flask.cli.with_appcontext
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
            assertion = auth_tokens.get_token(
                options.pop('user'),
                options.pop('password'),
                insecure=insecure,
            )

            lora.session.auth = auth_base.SAMLAuth(assertion)

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


@group.command('get')
@click.argument('paths', nargs=-1)
@requires_auth
def lora_get(paths):
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


@group.command('update')
@click.argument('path')
@click.argument('input', type=click.File('rb'), default='-')
@requires_auth
def lora_update(path, input):
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


@group.command('sheet-convert')
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


@group.command()
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output.')
@click.option('--minimal', is_flag=True,
              help='Just import the root unit.')
@click.option('--check', '-c', is_flag=True,
              help=('check if import would overwrite any existing '
                    'objects'))
@click.option('--delete', '-d', is_flag=True,
              help=('empty and delete organisation first'))
@flask.cli.with_appcontext
@requires_auth
def load(**kwargs):
    '''
    Import the sample fixtures into LoRA.
    '''

    from tests import util

    util.load_sample_structures(
        verbose=not kwargs.pop('quiet'),
        **kwargs,
    )
