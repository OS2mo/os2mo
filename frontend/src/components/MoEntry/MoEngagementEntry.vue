<template>
  <div>
    <b-form-checkbox
      class="mb-3 mt-1"
      data-vv-as="checkbox"
      v-model="entry.primary"
    >
      {{$t('input_fields.primary')}}
    </b-form-checkbox>

    <div class="form-row">
      <mo-organisation-unit-picker
        class="col"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
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
    </div>


    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />
  </div>
</template>

<script>
/**
 * A engagement entry component.
 */

import bFormCheckbox from 'bootstrap-vue/es/components/form-checkbox/form-checkbox'
import { MoInputDateRange } from '@/components/MoInput'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: 'MoEngagementEntry',

  components: {
    bFormCheckbox,
    MoInputDateRange,
    MoOrganisationUnitPicker,
    MoFacetPicker
  },

  props: {
    /**
     * Defines the validity.
     */
    validity: Object
  },

  computed: {
    /**
     * Hide the dates.
     */
    datePickerHidden () {
      return this.validity != null
    }
  },

  watch: {
    /**
     * Whenever entry change update.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'engagement'
        this.$emit('input', newVal)
      },
      deep: true
    },

    /**
     * When validity change update newVal.
     */
    validity (newVal) {
      this.entry.validity = newVal
    }
  }
}
</script>
