SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <mo-address-entry
    facet="org_unit_address_type"
    :value="value"
    :validityHidden="validityHidden"
    :required="required"
    :label="label"
    :disabled-dates="{ disabledDates }"
  />
</template>

<script>
/**
 * A manager address picker component.
 */

import { MoAddressEntry } from "@/components/MoEntry"

export default {
  name: "MoOrgUnitAddressEntry",
  extends: MoAddressEntry,

  components: {
    MoAddressEntry,
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    facet: {
      type: String,
      required: false,
    },
  },
}
</script>
