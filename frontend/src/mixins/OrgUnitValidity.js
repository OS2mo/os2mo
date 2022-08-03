// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

export default {
  computed: {
    orgUnitValidity() {
      if (this.entry.org_unit) {
        return this.entry.org_unit.validity
      }
    },
  },
}
