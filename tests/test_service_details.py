#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util


@util.mock()
class Tests(util.TestCase):
    def test_unit_redirect(self, m):
        self.assertRedirects(
            self.client.get(
                '/service/ou/00000000-0000-0000-0000-000000000000'
                '/details/info',
            ),
            '/service/ou/00000000-0000-0000-0000-000000000000/',
        )
