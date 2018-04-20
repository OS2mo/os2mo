<template>
  <div>
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="datePickerHidden"/>
    <div class="form-row">
      <mo-it-system-picker v-model="entry.itsystem" :preselected="entry.uuid"/>
    </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoItSystemPicker from '@/components/MoPicker/MoItSystemPicker'

export default {
  components: {
    MoDatePickerRange,
    MoItSystemPicker
  },
  props: {
    value: Object,
    validity: Object
  },
  data () {
    return {
      entry: {
        validity: {}
      }
    }
  },
  computed: {
    datePickerHidden () {
      return this.validity != null
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

