#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


from . import util


class Tests(util.TestCase):
    def test_failing_service(self):
        self.assertRequestResponse(
            '/service/kaflaflibob',
            {
                'message': 'no such endpoint',
                'error': True,
            },
            status_code=404,
        )
