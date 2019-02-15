
#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import sys

import flask

from mora.cli import base


def main(as_module=False):
    _, prog_name, *args = sys.argv

    base.cli.main(args=args, prog_name=prog_name)


if __name__ == '__main__':
    main()
