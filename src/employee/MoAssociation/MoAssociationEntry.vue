<template>
  <div>
      <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <mo-organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="entry.org_unit"
        />
        <mo-facet-picker facet="job_function" v-model="entry.job_function" required/>
        <mo-facet-picker facet="association_type" v-model="entry.association_type" required/>
        
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
      entry: {
        validity: {}
      }
    }
  },
  watch: {
    entry: {
      handler (newVal) {
        newVal.type = 'association'
        this.$emit('input', newVal)
      },
      deep: true
    },

    validity (newVal) {
      this.entry.validity = newVal
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>

