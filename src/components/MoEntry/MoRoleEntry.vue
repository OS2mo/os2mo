<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-picker
        class="col unit-role" 
        label="Vælg enhed" 
        v-model="entry.org_unit"
        required
      />
      <mo-facet-picker class="select-role" facet="role_type" v-model="entry.role_type" required/>
    </div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
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
