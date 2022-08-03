SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      class="from-date"
      v-model="entry.validity"
      :initially-hidden="validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <div class="form-row">
      <mo-organisation-unit-picker
        v-if="!hideOrgPicker"
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
        :extra-validations="validations"
      />

      <mo-facet-picker
        class="select-engagement_association"
        facet="engagement_association_type"
        v-model="entry.engagement_association_type"
        required
      />
    </div>
  </div>
</template>

<script>
/**
 * An engagement_association entry component.
 */

import { MoInputDateRange, MoInputText } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"
import { Employee } from "@/store/actions/employee"
import { mapGetters } from "vuex"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoEngagementAssociationEntry",

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
    ...mapGetters({
      currentEmployee: Employee.getters.GET_EMPLOYEE,
    }),

    validations() {
      return {
        existing_engagement_associations: [
          this.entry.org_unit,
          this.entry.validity,
          this.entry.uuid,
        ],
      }
    },
  },

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoInputText,
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "engagement_association"
        this.$emit("input", newVal)
      },
      deep: true,
    },
  },
}
</script>
