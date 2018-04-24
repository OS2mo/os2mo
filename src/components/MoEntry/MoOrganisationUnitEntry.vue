<template>
  <div>
      <mo-date-picker-range v-model="orgUnit.validity"/>

      <div class="form-row">
        <mo-input label="Navn" v-model="orgUnit.name" required/>
        
        <mo-facet-picker facet="org_unit_type" v-model="orgUnit.org_unit_type" required/>
      </div>
      
      <mo-organisation-unit-picker 
        v-model="orgUnit.parent" 
        :is-disabled="disableOrgUnitPicker"
        required
      />
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoInput from '@/components/atoms/MoInput'
import MoAddMany from '@/components/MoAddMany/MoAddMany'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoInput,
    MoAddMany
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    disableOrgUnitPicker: Boolean
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
