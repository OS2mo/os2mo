<template>
  <div>
      <mo-date-picker-range v-model="orgUnit.validity"/>

      <div class="form-row">
        <div class="form-group col">
          <label for="">Navn</label>
          <input 
            v-model="orgUnit.name" 
            data-vv-as="Navn"
            type="text" 
            class="form-control"
            name="unit-name"
            v-validate="{required: true}"
          >
          
          <span v-show="errors.has('unit-name')" class="text-danger">
            {{ errors.first('unit-name') }}
          </span>
        </div>
        
        <mo-facet-picker facet="org_unit_type" v-model="orgUnit.org_unit_type" required/>
      </div>
      
      <mo-organisation-unit-picker v-model="orgUnit.parent" :is-disabled="disableOrgUnitPicker"/>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoAddMany from '@/components/MoAddMany/MoAddMany'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
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
