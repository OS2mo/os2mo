<template>
  <div>
    <date-picker-start-end v-model="entry.validity" :initially-hidden="validityHidden"/>
    <div class="row">
    <organisation-unit-picker class="col" v-model="entry.org_unit" label="Angiv enhed"/>
    <mo-address-picker class="col" v-model="entry.address"/>
    </div> 
    <div class="form-row">
      <mo-facet-picker facet="manager_type" v-model="entry.manager_type"/>
      <mo-facet-picker facet="manager_level" v-model="entry.manager_level"/>  
      <mo-facet-picker facet="responsibility" v-model="entry.responsibility"/> 
    </div>
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'
import MoAddressPicker from '../../components/MoAddressPicker'

export default {
  components: {
    DatePickerStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker,
    MoAddressPicker
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
