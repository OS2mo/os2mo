SPDX-FileCopyrightText: 2021- Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <mo-employee-picker
      v-model="entry.owner"
      :label="$tc('input_fields.employee', 0)"
      class="search-employee mb-3"
      :validity="entry.validity"
      v-if="!hasInferencePriority"
    />

    <mo-input-select
      :display_method="display"
      v-model="entry.owner_inference_priority"
      :label="$t('input_fields.owner_inference_priority')"
      :options="inference_options"
      v-if="!hideOrgPicker && (!hasOwner || hasInferencePriority)"
    />
  </div>
</template>

<script>
/**
 * A owner entry component.
 */

import { MoInputDateRange, MoInputSelect } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import MoEntryBase from "./MoEntryBase.js"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"
import { display_method, inference_priority_values } from "../../helpers/ownerUtils"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoOwnerEntry",

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoEmployeePicker,
    MoInputSelect,
  },

  props: {
    /**
     * This boolean property hide the org picker.
     */
    hideOrgPicker: Boolean,

    /**
     * This boolean property hide the employee picker.
     */
    hideEmployeePicker: Boolean,
  },
  computed: {
    hasOwner() {
      return !!this.entry.owner
    },
    hasInferencePriority() {
      return !!this.entry.owner_inference_priority
    },
  },
  methods: {
    display(value) {
      return display_method(value)
    },
  },
  created() {
    this.inference_options = inference_priority_values
  },
  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        // clean-up before committing to backend: remove empty owner_inference_priority
        if (newVal.owner_inference_priority === "") {
          newVal.owner_inference_priority = undefined
        }
        // do not send owner field when owner was inferred
        if (newVal.owner && newVal.owner_inference_priority) {
          newVal.owner = undefined
        }
        newVal.type = "owner"
        this.$emit("input", newVal)
      },
      deep: true,
    },
  },
}
</script>
