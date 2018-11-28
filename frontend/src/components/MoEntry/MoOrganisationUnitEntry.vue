<template>
  <div>
      <div class="form-row">
        <mo-input
          :label="$t('input_fields.name')"
          v-model="orgUnit.name"
          required
        />

        <mo-facet-picker
          facet="org_unit_type"
          v-model="orgUnit.org_unit_type"
          required
        />
      </div>

      <mo-organisation-unit-picker
        v-model="orgUnit.parent"
        required
      />

      <mo-date-picker-range
        v-model="orgUnit.validity"
        :disable-to-date="!creatingDate"
      />
  </div>
</template>

<script>
/**
   * A organisation unit entry component.
   */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoInput from '@/components/atoms/MoInput'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoInput
  },

  /**
       * Validator scope, sharing all errors and validation state.
       */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: Object,

    /**
       * This boolean property able the date in create organisation component.
       */
    creatingDate: Boolean
  },

  data () {
    return {
      /**
        * The orgUnit component value.
        * Used to detect changes and restore the value.
        */
      orgUnit: {
        name: '',
        validity: {}
      }
    }
  },

  watch: {
    /**
       * Whenever orgUnit change, update newVal.
       */
    orgUnit: {
      handler (newVal) {
        this.$emit('input', newVal)
      },
      deep: true
    }
  },

  created () {
    /**
       * Called synchronously after the instance is created.
       * Set orgUnit to value.
       */
    this.orgUnit = this.value
  }
}
</script>
