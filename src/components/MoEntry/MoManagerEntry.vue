<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-search
        v-model="entry.org_unit" 
        label="Angiv enhed" 
        class="col"
        required
      />
      <mo-address-picker v-model="entry.address" :org-unit="entry.org_unit" class="col"/>
    </div> 
    <div class="form-row">
      <mo-facet-picker 
        facet="manager_type" 
        v-model="entry.manager_type" 
        required
      />
      <mo-facet-picker 
        facet="manager_level" 
        v-model="entry.manager_level"
        required
      />  
      <mo-facet-picker 
        facet="responsibility" 
        v-model="entry.responsibility"
        required
      /> 
    </div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitSearch,
    MoFacetPicker,
    MoAddressPicker
  },
  props: {
    value: Object,
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
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>
