#
# Copyright (c) 2017-2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json

import click

from . import spreadsheets


def run(output, sheets, compact, exact, **kwargs):
    '''Convert an Excel spreadsheet into JSON for faster importing

    '''

    del kwargs['jobs'], kwargs['target']

    if any(kwargs.values()):
        unsupported_args = [k for k in sorted(kwargs) if kwargs[k]]

        raise click.BadOptionUsage(
            'unsupported arguments: {}'.format(', '.join(unsupported_args)),
        )

    d = spreadsheets.load_data(sheets, exact=exact)

    if compact:
        json.dump(d, output)
    else:
        json.dump(d, output, indent=2, sort_keys=True)
