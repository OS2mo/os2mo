<template>
    <div class="form-group col">
      <label v-if="!noLabel" id="date-label" for="date">{{label}}</label>
      <date-time-picker 
        v-model="selected" 
        format="dd-MM-yyyy"
        :language="da"
        monday-first
        bootstrap-styling
        clear-button
        :disabled-dates="disabledDates"
        :disabled="disabled"
      />

      <input 
        :name="nameId"
        :data-vv-as="label" 
        v-model="date_string"
        type="hidden"
        v-validate="{required: required}">

      <span v-show="errors.has(nameId)" class="text-danger">{{ errors.first(nameId) }}</span>
    </div>
</template>

<script>

import DateTimePicker from 'vuejs-datepicker'
import { da } from 'vuejs-datepicker/dist/locale'

export default {
  components: {
    DateTimePicker
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: [Date, String],
    required: Boolean,
    noLabel: Boolean,
    label: {default: 'Dato', type: String},
    disabledTo: [Date, String],
    disabledFrom: [Date, String],
    disabled: Boolean
  },
  data () {
    return {
      disabledDates: {
        to: null,
        from: null
      },
      selected: null,
      date_string: null,
      da: da
    }
  },
  computed: {
    nameId () {
      return 'date-picker-' + this._uid
    }
  },
  watch: {
    selected (newVal) {
      // send on a date-only string in ISO format, so that we
      // disregard timezones and the time-of-day
      this.date_string = newVal ? this.$moment(new Date(newVal)).format('YYYY-MM-DD') : null
    },

    date_string (newVal) {
      this.$emit('input', newVal)
    },

    disabledTo (newVal) {
      this.disabledDates.to = newVal ? new Date(newVal) : null
    },

    disabledFrom (newVal) {
      this.disabledDates.from = newVal ? new Date(newVal) : null
    },

    value (newVal) {
      this.selected = newVal
    }
  },
  created () {
    this.selected = this.value
    this.date_string = this.value
  }
}
</script>
