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
        v-model="entry.org_unit"
        :label="$t('input_fields.select_unit')"
        class="col unit-manager"
        required
        v-if="!hideOrgPicker"
        :validity="entry.validity"
      />
    </div>

    <div class="form-row select-manager">
      <mo-facet-picker facet="kle_number" v-model="entry.kle_number" required />
    </div>

    <mo-add-many
      class="responsibility-manager"
      v-model="entry.kle_aspect"
      :entry-component="facetPicker"
      :label="$t('input_fields.kle_aspect')"
      has-initial-entry
      small-buttons
    />
  </div>
</template>

<script>
/**
 * A manager entry component.
 */

import { MoInputDateRange } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoAddMany from "@/components/MoAddMany/MoAddMany"
import MoEmployeePicker from "@/components/MoPicker/MoEmployeePicker"
import MoEntryBase from "./MoEntryBase.js"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoKLEEntry",

  components: {
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoAddMany,
    MoEmployeePicker,
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
    /**
     * Adds the facetPicker template to the add many component.
     */
    facetPicker() {
      return {
        components: {
          MoFacetPicker,
        },

        props: {
          value: Object,
        },

        data() {
          return {
            val: this.value,
          }
        },

        watch: {
          val(newVal) {
            this.$emit("input", newVal)
          },
        },

        template: `<div class="form-row"><mo-facet-picker facet="kle_aspect" v-model="val" required/></div>`,
      }
    },
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler(newVal) {
        newVal.type = "kle"
        this.$emit("input", newVal)
      },
      deep: true,
    },
  },
}
</script>
