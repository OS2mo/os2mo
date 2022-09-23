# SPDX-FileCopyrightText: 2015-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from oio_rest.custom_exceptions import DBException
from tests.oio_rest.util import BaseTestCase


class TestKubernetesProbes(BaseTestCase):
    """
    Test the Kubernetes liveness and readiness endpoints
    """

    def test_liveness(self):
        r = self.perform_request("/kubernetes/live")
        assert HTTP_204_NO_CONTENT == r.status_code

    @patch("oio_rest.kubernetes.object_exists")
    def test_readiness_everything_ready(self, mock_object_exists):
        mock_object_exists.return_value = False
        r = self.perform_request("/kubernetes/ready")

        assert HTTP_204_NO_CONTENT == r.status_code
        mock_object_exists.assert_called_once_with(
            "Organisation", "00000000-0000-0000-0000-000000000000"
        )

    @patch("oio_rest.kubernetes.object_exists")
    def test_readiness_db_not_ready(self, mock_object_exists):
        mock_object_exists.side_effect = DBException(0)
        r = self.perform_request("/kubernetes/ready")
        assert HTTP_503_SERVICE_UNAVAILABLE == r.status_code
