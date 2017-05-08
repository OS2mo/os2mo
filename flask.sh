#!/bin/sh
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

DIR=$(cd $(dirname $0); pwd)
VENV=$DIR/venv

if ! test -d $VENV
then
    python3.5 -m venv $VENV
fi

$VENV/bin/pip -q install -r requirements.txt

export PYTHONPATH="$DIR"
export FLASK_APP=mora.app
export FLASK_DEBUG=1

exec $VENV/bin/flask "$@"
