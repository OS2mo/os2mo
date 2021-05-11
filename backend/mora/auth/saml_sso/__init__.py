# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

# XXX: This is a terrible compatibility hack, to ensure we are able to resolve the
# existing sessions containing an enum from the original library
import sys
from . import session
sys.modules['flask_saml_sso'] = sys.modules[__name__]
sys.modules['flask_saml_sso.session'] = session

from .base import init_app # noqa
from .base import check_saml_authentication # noqa
from .base import get_session_attributes # noqa
from .base import get_session_name_id # noqa
