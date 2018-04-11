<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
    <mo-organisation-unit-picker v-model="entry.org_unit" label="Angiv enhed"/>
    <div class="form-row">
      <mo-facet-picker facet="manager_type" v-model="entry.manager_type"/>
      <mo-facet-picker facet="manager_level" v-model="entry.manager_level"/>  
      <mo-facet-picker facet="responsibility" v-model="entry.responsibility"/> 
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
        newVal.type = 'manager'
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
