#!/bin/sh -e

DIR=$(cd $(dirname $0); pwd)
VENV="$DIR"/venv

if ! test -d "$VENV"
then
    echo "Creating virtual environment!" >&2

    python3 -m venv "$VENV"

    "$VENV"/bin/pip install -qU packaging pip setuptools wheel
    "$VENV"/bin/pip install -qr "$DIR"/requirements-test.txt
fi

"$VENV"/bin/pip install -qe "$DIR"

export FLASK_ENV=development
export FLASK_APP="mora.app:create_app()"

exec "$VENV"/bin/python -m mora.cli "$0" "$@"
