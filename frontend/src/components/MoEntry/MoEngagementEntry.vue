SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden || validityHidden"
      :disabled-dates="{ orgUnitValidity, disabledDates }"
    />

    <div class="form-row">
      <mo-organisation-unit-picker
        class="col"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
      />

      <mo-input-text
        class="engagement_id"
        v-model="entry.user_key"
        :label="$t('input_fields.engagement_id')"
      />

      <mo-facet-picker
        facet="engagement_job_function"
        v-model="entry.job_function"
        required
      />

      <mo-facet-picker
        facet="engagement_type"
        v-model="entry.engagement_type"
        required
      />

      <mo-facet-picker
        v-if="showPrimary"
        facet="primary_type"
        v-model="entry.primary"
        required
      />
    </div>

    <div
      class="form-row"
      v-for="(v, row_index) in numberOfExtensionRows"
      :key="row_index"
    >
      <mo-input-text
        v-for="n in 2"
        v-if="extensionFields.length >= 2 * row_index + n"
        class="extension_field"
        v-model="entry['extension_' + (2 * row_index + n)]"
        :label="extensionFields[2 * row_index + n - 1]"
      />
    </div>
  </div>
</template>

<script>
/**
 * A engagement entry component.
 */

import { MoInputDateRange, MoInputText } from "@/components/MoInput"
import MoOrganisationUnitPicker from "@/components/MoPicker/MoOrganisationUnitPicker"
import MoFacetPicker from "@/components/MoPicker/MoFacetPicker"
import MoEntryBase from "./MoEntryBase"
import OrgUnitValidity from "@/mixins/OrgUnitValidity"

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: "MoEngagementEntry",

  components: {
    MoInputText,
    MoInputDateRange,
    MoOrganisationUnitPicker,
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
     * Hide the dates.
     */
    datePickerHidden() {
      return this.validity != null
    },
    showPrimary() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      return conf.show_primary_engagement
    },

    extensionFields() {
      let conf = this.$store.getters["conf/GET_CONF_DB"]
      let extension_labels = conf.extension_field_ui_labels.split(",")
      if (extension_labels.length > 0 && extension_labels[0] !== "") {
        return extension_labels
      }
      return []
    },

    numberOfExtensionRows() {
      let length = this.extensionFields.length
      let n_rows = Math.ceil(length / 2)
      return new Array(n_rows)
    },
  },

  watch: {
    /**
     * Whenever entry change update.
     */
    entry: {
      handler(newVal) {
        newVal.type = "engagement"
        this.$emit("input", newVal)
      },
      deep: true,
    },

    /**
     * When validity change update newVal.
     */
    validity(newVal) {
      this.entry.validity = newVal
    },
  },
}
</script>
