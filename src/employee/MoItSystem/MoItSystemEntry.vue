<template>
  <div>
      <date-start-end v-model="itSystem.validity" initially-hidden/>
      <div class="form-row">
        <it-system-picker v-model="itSystem.itsystem"/>
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
    validity: Object
  },
  data () {
    return {
      itSystem: {
        validity: {}
      }
    }
  },
  watch: {
    itSystem (newVal) {
      newVal.type = 'it'
      this.$emit('input', newVal)
      let valid = false
      if (Object.keys(newVal).length >= 3 && newVal.validity.from !== undefined) valid = true
      this.$emit('is-valid', valid)
    },

    validity (newVal) {
      this.itSystem.validity = newVal
    }
  },
  created () {
    this.itSystem = this.value
  }
}
</script>

