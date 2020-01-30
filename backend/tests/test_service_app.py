# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from unittest import mock

from tests import util


class Tests(util.TestCase):
    def test_failing_service(self):
        self.assertRequestResponse(
            '/service/kaflaflibob',
            {
                'error': True,
                'error_key': 'E_NO_SUCH_ENDPOINT',
                'description': 'No such endpoint.',
                'status': 404,
            },
            status_code=404,
        )

    @mock.patch('mora.common.get_connector')
    def test_exception_handling(self, p):
        p.side_effect = ValueError('go away')

        self.assertRequestResponse(
            '/service/ou/00000000-0000-0000-0000-000000000000/',
            {
                'error': True,
                'error_key': 'E_UNKNOWN',
                'description': 'go away',
                'status': 500,
            },
            status_code=500,
            drop_keys=['stacktrace'],
        )

    def test_restrictargs_everywhere(self):
        unfiltered = {
            viewname
            for viewname, viewfunc in self.app.view_functions.items()
            if '.' in viewname and not hasattr(viewfunc, 'restricts_args')
        }

        print('\n'.join(sorted(unfiltered)))

        self.assertFalse(unfiltered,
                         'no blueprints may have unrestricted arguments!')
