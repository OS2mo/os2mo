<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-association"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
      />

      <mo-address-picker
        class="col address-association"
        v-model="entry.address"
        :org-unit="entry.org_unit"
      />
    </div>

    <div class="form-row select-association">
      <mo-facet-picker
        facet="job_function"
        v-model="entry.job_function"
        required
      />

      <mo-facet-picker
        facet="association_type"
        v-model="entry.association_type"
        required
      />
    </div>

    <mo-date-picker-range
      v-model="entry.validity"
      :initially-hidden="validityHidden"
    />
  </div>
</template>

<script>
/**
 * A association entry component.
 */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoAddressPicker,
    MoFacetPicker
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * This boolean property hides the validity.
     */
    validityHidden: Boolean
  },

  data () {
    return {
      /**
       * The entry component value.
       * Used to detect changes and restore the value.
       */
      entry: {
        validity: {}
      }
    }
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'association'
        this.$emit('input', newVal)
      },
      deep: true
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
