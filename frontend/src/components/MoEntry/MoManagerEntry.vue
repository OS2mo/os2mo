<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        v-model="entry.org_unit" 
        label="Angiv enhed" 
        class="col unit-manager"
        required
      />

      <mo-address-picker 
        class="col address-manager" 
        v-model="entry.address" 
        :org-unit="entry.org_unit"
      />
    </div>

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
      label="Lederansvar" 
      has-initial-entry 
      small-buttons
    />
    
    <mo-date-picker-range 
      v-model="entry.validity" 
      :initially-hidden="validityHidden"
    /> 
  </div>
</template>

<script>
  /**
   * A manager entry component.
   */

  import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
  import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'
  import MoAddMany from '@/components/MoAddMany/MoAddMany'

  export default {
    components: {
      MoDatePickerRange,
      MoOrganisationUnitPicker,
      MoFacetPicker,
      MoAddressPicker,
      MoAddMany
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * This boolean property hides validity.
       */
      validityHidden: Boolean
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
       * Adds the facetPicker to the add many component.
       */
      facetPicker () {
        return {
          components: { MoFacetPicker },
          props: { value: Object },
          data () { return { val: null } },
          watch: { val (newVal) { this.$emit('input', newVal) } },
          created () { this.val = this.value },
          template: `<div class="form-row"><mo-facet-picker facet="responsibility" v-model="val" required/></div>`
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
