# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def get_session(bind):
    """Provide a transactional scope around a series of operations."""
    session = Session(bind=bind)
    try:
        yield session
        session.commit()
    except Exception as exp:
        session.rollback()
        raise exp
    finally:
        session.close()
