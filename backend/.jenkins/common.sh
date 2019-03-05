# -*- mode: sh; sh-shell: bash -*-

set -ex

export OS2MO_DUMMY_MODE=true

TOPDIR=$(cd "$(dirname ${BASH_SOURCE[0]})"/../..; pwd)

if test -z "$VENV"
then
    VENV="$TOPDIR/backend/venv"
fi

if test ${WANT_VENV:=1} != 0
then
    python3 -m venv "$VENV"

    export PATH="$VENV/bin:$PATH"
fi
