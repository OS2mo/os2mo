<template>
  <div>
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

    <mo-date-picker-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden"
      :disabled-dates="orgUnitValidity"
    />
  </div>
</template>

<script>
/**
 * A engagement entry component.
 */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'

export default {
  extends: MoEntryBase,
  name: 'MoEngagementEntry',
  components: {
    MoDatePickerRange,
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
    },

    /**
     * Disabled organisation dates.
     */
    orgUnitValidity () {
      if (this.entry.org_unit) {
        let validityCopy = Object.assign({}, this.entry.org_unit.validity)
        if (validityCopy.from < this.disabledDates.from) {
          validityCopy.from = this.disabledDates.from
        }
        return validityCopy
      }
      return this.disabledDates
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
