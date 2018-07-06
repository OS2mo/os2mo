<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-search 
        class="col" 
        label="Vælg enhed" 
        v-model="entry.org_unit"
        required
      />
      <mo-facet-picker facet="role_type" v-model="entry.role_type" required/>
    </div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitSearch,
    MoFacetPicker
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
        newVal.type = 'role'
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
