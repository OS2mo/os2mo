# -*- mode: sh; sh-shell: bash -*-

set -ex

TOPDIR=$(cd "$(dirname ${BASH_SOURCE[0]})"/../..; pwd)
GIT_COMMIT=$(GIT_DIR="$TOPDIR/.git" git rev-parse --short HEAD)

if test -z "$VENV"
then
    VENV="$TOPDIR/venv"
fi

if test ${WANT_VENV:=1} != 0
then
    python3 -m venv "$VENV"

    export PATH="$VENV/bin:$PATH"
fi
