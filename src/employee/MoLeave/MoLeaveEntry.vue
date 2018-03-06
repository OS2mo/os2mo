<template>
  <div>
    <date-picker-start-end v-model="entry.validity" :initially-hidden="validityHidden"/>   
    <leave-picker :org="org" v-model="entry.leave_type"/> 
    <mo-facet-picker facet="leave_type" label="Orlovstype" v-model="entry.leave_type"/>
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import LeavePicker from '../../components/LeavePicker'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DatePickerStartEnd,
    LeavePicker,
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
        newVal.type = 'leave'
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 3 && Object.keys(newVal.validity).length === 2)
        this.$emit('is-valid', valid)
      },
      deep: true
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>
