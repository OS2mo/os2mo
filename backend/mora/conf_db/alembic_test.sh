#!/bin/bash
if initial=$(alembic heads); then
  if alembic revision --autogenerate; then
    if final=$(alembic heads); then
      if [ "$initial" == "$final" ]; then
        exit 0
      fi
    fi
  fi
fi
exit 1

