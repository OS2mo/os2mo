# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# Writes are governed by the "admin" role, reads by the "reader" role
# "owner" grants write access to owned entities via the owner write rules
ALL_PERMISSIONS = {"admin", "reader", "owner"}
