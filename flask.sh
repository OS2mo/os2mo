#!/bin/sh

export FLASK_APP=mora.app
export FLASK_DEBUG=1

DIR=$(cd $(dirname $0); pwd)

if ! test -d $DIR/env
then
    python3.5 -m venv $DIR/env
fi

export PYTHONPATH="$DIR"

$DIR/env/bin/pip -q install -r requirements.txt

exec $DIR/env/bin/flask "$@"
