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
      v-model="dateString"
      type="hidden"
      v-validate="{required: required, date_in_range: validDates}">

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
    validDates: Object,
    disabled: Boolean
  },
  data () {
    return {
      selected: null,
      dateString: null,
      da: da
    }
  },
  computed: {
    nameId () {
      return 'date-picker-' + this._uid
    },

    disabledDates () {
      return {
        from: this.validDates.to ? this.validDates.to : null,
        to: this.validDates.from ? this.validDates.from : null
      }
    }
  },
  watch: {
    selected (newVal) {
      // send on a date-only string in ISO format, so that we
      // disregard timezones and the time-of-day
      this.dateString = newVal ? this.$moment(new Date(newVal)).format('YYYY-MM-DD') : null
    },

    disabledDates: {
      handler (newVal) {
        this.$validator.validate(this.nameId)
      },
      deep: true
    },

    dateString (newVal) {
      this.$emit('input', newVal)
    },

    value (newVal) {
      this.selected = newVal
    }
  },
  created () {
    this.selected = this.value
    this.dateString = this.value
  }
}
</script>
