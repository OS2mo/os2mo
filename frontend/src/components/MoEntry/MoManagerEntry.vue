<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        v-model="entry.org_unit" 
        label="Angiv enhed" 
        class="col unit-manager"
        required
      />
    </div>

      <mo-add-many
        class="address-manager"
        v-model="entry.address"
        :entry-component="managerAddressPicker"
        label="Lederadressetype"
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
      label="Lederansvar" 
      has-initial-entry 
      small-buttons
    />
    
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
  </div>
</template>

<script>
  import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
  import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'
  import MoAddMany from '@/components/MoAddMany/MoAddMany'
  import MoManagerAddressPicker from '@/components/MoPicker/MoManagerAddressPicker'
  import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

  export default {
    components: {
      MoDatePickerRange,
      MoOrganisationUnitPicker,
      MoFacetPicker,
      MoAddressPicker,
      MoAddMany,
      MoManagerAddressPicker,
      MoAddressEntry
    },

    props: {
      value: Object,
      validityHidden: Boolean
    },

    data () {
      return {
        entry: {}
      }
    },

    computed: {
      datePickerHidden () {
        return this.validity != null
      },

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
              val: null
            }
          },

          watch: {
            val (newVal) {
              this.$emit('input', newVal)
            }
          },

          created () {
            this.val = this.value
          },

          template: `<div class="form-row"><mo-facet-picker facet="responsibility" v-model="val" required/></div>`
        }
      },

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

          watch: {
            val (newVal) {
              this.val = this.value instanceof Array ? this.value[0] : this.value
              this.$emit('input', newVal)
            }
          },

          created () {
            this.val = this.value
          },

          template: `<mo-manager-address-picker v-model="val" required/>`
        }
      }
    },

    watch: {
      entry: {
        handler (newVal) {
          newVal.type = 'manager'
          this.$emit('input', newVal)
        },
        deep: true
      }
    },

    created () {
      this.entry = this.value
    }
  }
</script>
