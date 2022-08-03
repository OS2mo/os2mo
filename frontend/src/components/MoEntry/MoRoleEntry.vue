SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-role"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
      />

      <mo-facet-picker
        class="select-role"
        facet="role_type"
        v-model="entry.role_type"
        required
      />
    </div>
  </div>
</template>

<script>
/**
 * A role entry component.
 */

import { MoInputDateRange } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoRoleEntry",

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "role"
        this.$emit("input", newVal)
      },
      deep: true,
    },
  },
}
</script>
