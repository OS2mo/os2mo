#!/bin/sh

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
