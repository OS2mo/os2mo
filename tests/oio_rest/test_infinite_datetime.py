# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from datetime import timedelta

import pytest
from oio_rest.db.quick_query.search import InfiniteDatetime

INFINITY = "infinity"
NINFINITY = "-infinity"


class TestInfiniteDatetime:
    def test_parsing(self):
        base = datetime.now()
        base_str = base.isoformat()

        assert base_str == InfiniteDatetime.from_datetime(base).value
        assert base_str == InfiniteDatetime.from_date_string(base_str).value
        assert INFINITY == InfiniteDatetime.from_date_string(INFINITY).value
        assert NINFINITY == InfiniteDatetime.from_date_string(NINFINITY).value

    def test_comparison(self):
        base = datetime.now()

        ninf = InfiniteDatetime.from_date_string(NINFINITY)
        small = InfiniteDatetime.from_datetime(base)
        greater = InfiniteDatetime.from_datetime(base + timedelta(seconds=1))
        inf = InfiniteDatetime.from_date_string(INFINITY)

        # assert small to large
        assert ninf < small
        assert ninf < greater
        assert ninf < inf

        assert small < greater
        assert small < inf

        assert greater < inf

        # assert large to small
        assert not (inf < greater)
        assert not (inf < small)
        assert not (inf < ninf)

        assert not (greater < small)
        assert not (greater < ninf)

        assert not (small < ninf)

        # illegal asserts
        with pytest.raises(ValueError):
            ninf < ninf
        with pytest.raises(ValueError):
            inf < inf

        # Type asserts
        with pytest.raises(TypeError):
            small < base
        with pytest.raises(TypeError):
            small < base.isoformat()
