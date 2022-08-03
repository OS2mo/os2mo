SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden || validityHidden"
      :disabled-dates="{ disabledDates }"
    />

    <div class="form-row">
      <mo-facet-picker facet="leave_type" v-model="entry.leave_type" required />
    </div>

    <div class="form-row">
      <mo-engagement-picker
        class="mt-3"
        v-model="entry.engagement"
        :employee="entry.person"
        required
      />
    </div>
  </div>
</template>

<script>
/**
 * A leave entry component.
 */

import { MoInputDateRange } from "@/components/MoInput"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoEngagementPicker from "@/components/MoPicker/MoEngagementPicker"
import MoEntryBase from "./MoEntryBase"

export default {
  extends: MoEntryBase,
  name: "MoLeaveEntry",
  components: {
    MoInputDateRange,
    MoEngagementPicker,
    MoFacetPicker,
  },

  props: {
    /**
     * Defines the validity.
     */
    validity: Object,
  },

  computed: {
    /**
     * Hides the validity.
     */
    datePickerHidden() {
      return this.validity != null
    },
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "leave"
        this.$emit("input", newVal)
      },
      deep: true,
    },

    /**
     * When validity change, update newVal.
     */
    validity(newVal) {
      this.entry.validity = newVal
    },
  },
}
</script>
