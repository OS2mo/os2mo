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

    inject: {
      $validator: '$validator'
    },

    props: {
      value: Object,
      disableOrgUnitPicker: Boolean,
      creatingDate: Boolean
    },

    data () {
      return {
        orgUnit: {
          name: '',
          validity: {}
        }
      }
    },

    watch: {
      orgUnit: {
        handler (newVal) {
          this.$emit('input', newVal)
        },
        deep: true
      }
    },

    created () {
      this.orgUnit = this.value
    }
  }
</script>
