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
        facet="job_function"
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

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: Object,

    /**
       * Defines the validity.
       */
    validity: Object
  },

  data () {
    return {
      /**
        * The entry component value.
        * Used to detect changes and restore the value.
        */
      entry: {}
    }
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
        return this.entry.org_unit.validity
      }
      return {}
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
  },

  created () {
    /**
       * Called synchronously after the instance is created.
       * Set entry to value.
       */
    this.entry = this.value
  }
}
</script>
