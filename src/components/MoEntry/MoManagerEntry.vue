<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="datePickerHidden"/> 
    <div class="form-row">
      <mo-organisation-unit-picker v-model="entry.org_unit" label="Angiv enhed"/>
      <mo-address-picker v-model="entry.address" :org-unit="entry.org_unit"/>
    </div> 
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
import MoAddressPicker from '@/components/MoAddressPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoFacetPicker,
    MoAddressPicker
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
  computed: {
    datePickerHidden () {
      return this.validity != null
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
