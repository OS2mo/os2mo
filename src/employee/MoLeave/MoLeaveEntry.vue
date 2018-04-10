<template>
  <div>
    <date-picker-start-end v-model="entry.validity" :initially-hidden="validityHidden"/>   
    <mo-facet-picker facet="leave_type" v-model="entry.leave_type" required/>
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {

  components: {
    DatePickerStartEnd,
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
