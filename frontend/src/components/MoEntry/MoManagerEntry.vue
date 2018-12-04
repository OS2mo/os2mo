<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        v-model="entry.org_unit"
        :label="$t('input_fields.select_unit')"
        class="col unit-manager"
        required
        v-if="!hideOrgPicker"
      />
    </div>

      <label v-if="!hideEmployeePicker">{{$tc('input_fields.employee_optional')}}</label>
      <mo-employee-picker
        v-model="entry.person"
        class="search-employee mb-3"
        v-if="!hideEmployeePicker"
        noLabel
      />

      <mo-add-many
        class="address-manager"
        v-model="entry.address"
        :entry-component="managerAddressPicker"
        :label="$t('input_fields.manager_address_type')"
        has-initial-entry
        small-buttons
      />

    <div class="form-row select-manager">
      <mo-facet-picker
        facet="manager_type"
        v-model="entry.manager_type"
        required
      />

      <mo-facet-picker
        facet="manager_level"
        v-model="entry.manager_level"
        required
      />
    </div>

    <mo-add-many
      class="responsibility-manager"
      v-model="entry.responsibility"
      :entry-component="facetPicker"
      :label="$t('input_fields.manager_responsibility')"
      has-initial-entry
      small-buttons
    />

    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
  </div>
</template>

<script>
/**
 * A manager entry component.
 */

import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoAddMany from '@/components/MoAddMany/MoAddMany'
import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
import MoManagerAddressPicker from '@/components/MoPicker/MoManagerAddressPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoAddMany,
    MoEmployeePicker
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * This boolean property hides validity.
     */
    validityHidden: Boolean,

    /**
     * This boolean property hide the org picker.
     */
    hideOrgPicker: Boolean,

    /**
     * This boolean property hide the employee picker.
     */
    hideEmployeePicker: Boolean
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
     * Hides the validity.
     */
    datePickerHidden () {
      return this.validity != null
    },

    /**
     * Adds the facetPicker template to the add many component.
     */
    facetPicker () {
      return {
        components: {
          MoFacetPicker
        },

        props: {
          value: Object
        },

        data () {
          return {
            val: this.value
          }
        },

        watch: {
          val (newVal) {
            this.$emit('input', newVal)
          }
        },

        template: `<div class="form-row"><mo-facet-picker facet="responsibility" v-model="val" required/></div>`
      }
    },

    /**
     * Adds the managerAddressPicker template to the add many component.
     */
    managerAddressPicker () {
      return {
        components: {
          MoManagerAddressPicker
        },

        props: {
          value: [Object, Array]
        },

        data () {
          return {
            val: this.value
          }
        },

        template: `<mo-manager-address-picker v-model="val" required/>`
      }
    }
  },

  watch: {
    /**
     * Whenever entry change, update newVal.
     */
    entry: {
      handler (newVal) {
        newVal.type = 'manager'
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
