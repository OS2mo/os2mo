<template>
  <div>
    <date-picker-start-end v-model="entry.validity" initially-hidden/> 
    <organisation-unit-picker v-model="entry.org_unit"/>
    <div class="form-row">
      <mo-facet-picker facet="manager_type" label="Ledertype" v-model="entry.manager_type" required/>
      <mo-facet-picker facet="manager_level" label="Lederniveau" v-model="entry.manager_level" required/>  
      <mo-facet-picker facet="responsibility" label="Lederansvar" v-model="entry.responsibility" required/> 
    </div>
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DatePickerStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker
  },
  props: {
    value: Object,
    validity: Object
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
        let valid = (Object.keys(newVal).length >= 6 && newVal.validity.from !== undefined)
        this.$emit('is-valid', valid)
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
