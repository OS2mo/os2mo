#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Management utility for MORA.

'''


import functools
import json
import sys

import click
import flask
import flask_saml_sso

from . import base
from .. import exceptions
from .. import lora


@base.cli.group('lora')
def group():
    '''Subcommands for interacting directly with LoRA.'''


def requires_auth(func):
    @click.option('--token', '-t',
                  help="API token")
    @flask.cli.with_appcontext
    def wrapper(*args, **options):
        lora.session.auth = flask_saml_sso.SAMLAuth(options.pop('token'))

        return func(*args, **options)

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
