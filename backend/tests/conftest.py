# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os

from hypothesis import strategies as st

from mora.api.v1.models import Validity
from tests.hypothesis_utils import validity_model_strat


def pytest_runtest_setup(item):
    print(os.environ.items())
    os.environ['PYTEST_RUNNING'] = 'True'


st.register_type_strategy(
    Validity, validity_model_strat()
)
