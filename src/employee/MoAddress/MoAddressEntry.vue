<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
    <div class="form-row">
      <mo-facet-picker facet="address_type" v-model="entry.address_type" required/>
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
    org: {
      type: Object,
      required: true
    },
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
        newVal.type = 'address'
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
