<template>
  <div>
      <mo-date-picker-range v-model="association.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <mo-organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.org_unit"
        />
        <mo-facet-picker facet="job_function" v-model="association.job_function" required/>
        <mo-facet-picker facet="association_type" v-model="association.association_type" required/>
        
      </div>
  </div>
</template>

<script>
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
    value: Object,
    validity: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      association: {
        validity: {}
      }
    }
  },
  watch: {
    association: {
      handler (newVal) {
        newVal.type = 'association'
        this.$emit('input', newVal)
      },
      deep: true
    },

    validity (newVal) {
      this.association.validity = newVal
    }
  },
  created () {
    this.association = this.value
  }
}
</script>

