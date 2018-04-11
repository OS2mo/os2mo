<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>   
    <mo-facet-picker facet="leave_type" v-model="entry.leave_type" required/>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoFacetPicker from '@/components/MoFacetPicker'

export default {

  components: {
    MoDatePickerRange,
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
        newVal.type = 'leave'
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
