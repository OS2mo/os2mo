#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


def publish_message(domain, action, object_type, domain_uuid):
    """Dummy function for sending AMQP messages."""
    print("[%s.%s.%s] %s" % (domain, action, object_type, domain_uuid))
