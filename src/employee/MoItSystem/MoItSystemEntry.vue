<template>
  <div>
      <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <it-system-picker v-model="entry.itsystem" :preselected="entry.uuid"/>
      </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import ItSystemPicker from '@/components/ItSystemPicker'

export default {
  components: {
    MoDatePickerRange,
    ItSystemPicker
  },
  props: {
    value: Object,
    validity: Object,
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
        newVal.type = 'it'
        if (newVal.itsystem !== undefined) newVal.uuid = newVal.itsystem.uuid
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

