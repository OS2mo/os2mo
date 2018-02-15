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
        type: 'it',
        validity: {}
      }
    }
  },
  watch: {
    itSystem (newVal) {
      this.$emit('input', newVal)
    },

    validity (newVal) {
      this.itSystem.validity = newVal
    }
  },
  created () {
    this.itSystem.itsystem = this.value
  }
}
</script>

