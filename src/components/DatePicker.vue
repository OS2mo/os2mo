<template>
    <div class="form-group col">
      <label v-if="!noLabel" id="date-label" for="date">{{label}}</label>
      <date-time-picker 
        name="date-picker"
        :data-vv-as="label"
        v-model="selected" 
        format="dd-MM-yyyy"
        language="da" 
        monday-first
        bootstrapStyling
        clear-button
        :disabled="disabled"
        v-validate="{ required: true }"
      />

      <span
        v-show="errors.has('date-picker')" 
        class="text-danger"
      >
        {{ errors.first('date-picker') }}
      </span>
    </div>
</template>

<script>

import DateTimePicker from 'vuejs-datepicker'

export default {
  components: {
    DateTimePicker
  },
  props: {
    value: [Date, String],
    required: Boolean,
    noLabel: Boolean,
    label: {
      default: 'Dato',
      type: String
    },
    disabledTo: [Date, String],
    disabledFrom: [Date, String]
  },
  data () {
    return {
      disabled: {
        to: null,
        from: null
      },
      selected: null
    }
  },
  watch: {
    selected (newVal) {
      if (newVal != null) newVal.setUTCHours(0, 0, 0, 0)
      this.$emit('input', newVal)
    },

    disabledTo (newVal) {
      this.disabled.to = newVal ? new Date(newVal) : null
    },

    disabledFrom (newVal) {
      this.disabled.from = newVal ? new Date(newVal) : null
    },

    value (newVal) {
      this.selected = newVal
    }
  },
  created () {
    this.selected = this.value ? new Date(this.value) : null
  }
}
</script>
