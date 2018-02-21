<template>
  <div>
    <date-picker-start-end v-model="leave.validity"/>   
    <leave-picker :org="org" v-model="leave.leave_type"/>  
  </div>
</template>

<script>
import DatePickerStartEnd from '../../components/DatePickerStartEnd'
import LeavePicker from '../../components/LeavePicker'

export default {
  components: {
    DatePickerStartEnd,
    LeavePicker
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      leave: {}
    }
  },
  watch: {
    leave: {
      handler (newVal) {
        newVal.type = 'leave'
        this.$emit('input', newVal)
        let valid = false
        if (Object.keys(newVal).length >= 3 && newVal.validity.from !== undefined) valid = true
        this.$emit('is-valid', valid)
      },
      deep: true
    }
  },
  created () {
    this.leave = this.value
  }
}
</script>
