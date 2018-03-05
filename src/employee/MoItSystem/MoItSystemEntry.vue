<template>
  <div>
      <date-start-end v-model="entry.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <it-system-picker v-model="entry.itsystem"/>
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import ItSystemPicker from '../../components/ItSystemPicker'

export default {
  components: {
    DateStartEnd,
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
        this.$emit('input', newVal)
        let valid = (Object.keys(newVal).length >= 3 && newVal.validity.from !== undefined)
        this.$emit('is-valid', valid)
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

