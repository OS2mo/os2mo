<template>
  <mo-address-entry
    facet="manager_address_type"
    :value="value"
    :validityHidden="validityHidden"
    :required="required"
    :label="label"
    :preselectedType="preselectedType"
  ></mo-address-entry>
</template>

<script>
/**
 * A manager address picker component.
 */

import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

export default {
  name: 'MoManagerAddressEntry',
  extends: MoAddressEntry,

  components: {
    MoAddressEntry
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: [Object, Array],

    /**
     * This boolean property hides the validity dates.
     */
    validityHidden: Boolean,

    /**
     * This boolean property requires a selected address type.
     */
    required: Boolean,

    /**
     * Defines a label.
     */
    label: String,

    /**
     * Defines a preselectedType.
     */
    preselectedType: String
  }
}
</script>
