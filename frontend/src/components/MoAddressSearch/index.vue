SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="mo-address-search">
    <div class="form-row">
      <mo-address-search-field
        class="mb-0"
        v-model="internalValue"
        :label="label"
        :global="global"
        :required="required"
      />

      <label class="form-check-label">
        <input class="form-check-input" type="checkbox" v-model="global" />
        {{ $t("input_fields.search_entire_country") }}
      </label>
    </div>
  </div>
</template>

<script>
/**
 * Address search component.
 */

import MoAddressSearchField from "./MoAddressSearchField"
import MoInputBase from "@/components/MoInput/MoInputBase"

export default {
  extends: MoInputBase,
  components: {
    MoAddressSearchField,
  },
  data() {
    return {
      /**
       * Search globally
       * @type {Boolean}
       */
      global: false,
    }
  },
}
</script>
