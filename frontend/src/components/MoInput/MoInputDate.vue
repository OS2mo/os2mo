<template>
  <div class="form-group">
    <label v-if="hasLabel" :for="identifier">{{label}}</label>

    <date-time-picker
      v-model="internalValue"
      :open-date="initialValue"
      format="dd-MM-yyyy"
      :language="da"
      monday-first
      bootstrap-styling
      clear-button
      :disabled-dates="disabledDates"
      :disabled="disabled"
    />

    <input
      :name="identifier"
      :data-vv-as="label"
      v-model="internalValue"
      type="hidden"
      v-validate="{required: required, date_in_range: validDates}"
    >

    <span v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * A date picker component.
 */

import DateTimePicker from 'vuejs-datepicker'
import { da } from 'vuejs-datepicker/dist/locale'
import moment from 'moment'
import MoInputBase from './MoInputBase'

export default {
  extends: MoInputBase,
  name: 'MoInputDate',
  components: {
    DateTimePicker
  },

  props: {
    /**
     * Set valid date interval
     * @default null
     * @type {Object}
     */
    validDates: Object
  },

  data () {
    return {
      /**
       * Danish language translation for date picker
       */
      da: da
    }
  },

  computed: {
    /**
     * The initially focused value. Use either the current value or the
     * closest allowed value.
     */
    initialValue () {
      let currentDate = this.internalValue ? new Date(this.internalValue) :
      new Date()
      let disabled = this.disabledDates

      if (disabled.to && currentDate <= disabled.to)
        return disabled.to
      else if (disabled.from && currentDate < disabled.from)
        return disabled.from
      else
        return currentDate
    },

    /**
     * Date interval to disable.
     * We flip the validTo dates, as we want to disable anything outside of the range.
     * @type {Object}
     */
    disabledDates () {
      return {
        from: this.validDates && this.validDates.to ? new Date(this.validDates.to) : null,
        to: this.validDates && this.validDates.from ? new Date(this.validDates.from) : null
      }
    }
  },

  watch: {
    /**
     * Send on a date-only string in ISO format, so that we
     * disregard timezones and the time-of-day.
     */
    internalValue (newVal) {
      let modifiedValue = newVal ? moment(new Date(newVal)).format('YYYY-MM-DD') : null
      this.$emit('input', modifiedValue)
    }
  }
}
</script>
