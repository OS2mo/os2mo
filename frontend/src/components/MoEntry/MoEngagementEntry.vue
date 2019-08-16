<template>
  <div>
    <mo-input-date-range
      v-model="entry.validity"
      :initially-hidden="datePickerHidden"
      :disabled-dates="{orgUnitValidity, disabledDates}"
    />

    <mo-input-checkbox
      v-model="entry.primary"
      :data-vv-as="$t('input_fields.primary_engagement')"
    />

    <div class="form-row">
      <mo-organisation-unit-picker
        class="col"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
        :validity="entry.validity"
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
  </div>
</template>

<script>
/**
 * A engagement entry component.
 */

import { MoInputDateRange } from '@/components/MoInput'
import MoInputCheckbox from '@/components/MoInput/MoInputCheckbox'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoEntryBase from './MoEntryBase'
import OrgUnitValidity from '@/mixins/OrgUnitValidity'

export default {
  mixins: [OrgUnitValidity],

  extends: MoEntryBase,

  name: 'MoEngagementEntry',

  components: {
    MoInputCheckbox,
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
