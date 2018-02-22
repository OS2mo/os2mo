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
      leave: {
        validity: {}
      }
    }
  },
  watch: {
    leave: {
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
    this.leave = this.value
  }
}
</script>
