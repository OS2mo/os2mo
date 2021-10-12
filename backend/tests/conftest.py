# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import os

from hypothesis import strategies as st
from hypothesis import Verbosity, settings as h_settings

from mora.api.v1.models import Validity
from tests.hypothesis_utils import validity_model_strat


h_settings.register_profile("ci", max_examples=100, deadline=None)
h_settings.register_profile("dev", max_examples=10)
h_settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)
h_settings.load_profile(os.getenv(u"HYPOTHESIS_PROFILE", "default"))


def pytest_runtest_setup(item):
    print(os.environ.items())
    os.environ['PYTEST_RUNNING'] = 'True'


st.register_type_strategy(
    Validity, validity_model_strat()
)
