<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
    <organisation-unit-picker v-model="entry.org_unit" label="Angiv enhed"/>
    <div class="form-row">
      <mo-facet-picker facet="manager_type" v-model="entry.manager_type"/>
      <mo-facet-picker facet="manager_level" v-model="entry.manager_level"/>  
      <mo-facet-picker facet="responsibility" v-model="entry.responsibility"/> 
    </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import OrganisationUnitPicker from '@/components/OrganisationUnitPicker'
import MoFacetPicker from '@/components/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    OrganisationUnitPicker,
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
