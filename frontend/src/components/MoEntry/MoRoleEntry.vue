<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-role"
        :label="$t('input_fields.select_unit')"
        v-model="entry.org_unit"
        required
      />

      <mo-facet-picker
        class="select-role"
        facet="role_type"
        v-model="entry.role_type"
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
   * A role entry component.
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
        newVal.type = 'role'
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
