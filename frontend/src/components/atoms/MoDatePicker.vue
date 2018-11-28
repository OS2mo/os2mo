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
      v-validate="{required: required, date_in_range: validDates}"
    >

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
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

export default {
  components: {
    DateTimePicker
  },

  /**
       * Validator scope, sharing all errors and validation state.
       */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: [Date, String],

    /**
       * This boolean property requires a date.
       */
    required: Boolean,

    /**
       * This boolean property hides the label.
       */
    noLabel: Boolean,

    /**
       * Defines the label.
       */
    label: { default: 'Dato', type: String },

    /**
       * Defines valid dates.
       */
    validDates: Object,

    /**
       * This boolean disable the dates.
       */
    disabled: Boolean
  },

  data () {
    return {
      /**
        * The selected, dateString, da component value.
        * Used to detect changes and restore the value.
        */
      selected: null,
      dateString: null,
      da: da
    }
  },

  computed: {
    /**
       * Get name `date-picker`.
       */
    nameId () {
      return 'date-picker-' + this._uid
    },

    /**
       * Disable the choosen from date and the to date.
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
    selected (newVal) {
      this.dateString = newVal ? moment(new Date(newVal)).format('YYYY-MM-DD') : null
    },

    /**
       * Whenever dateString change, update newVal.
       */
    dateString (newVal) {
      this.$emit('input', newVal)
    },

    /**
       * When value change update selected to newVal.
       */
    value (newVal) {
      this.selected = newVal
    }
  },

  created () {
    /**
       * Called synchronously after the instance is created.
       * Set selected and dateString to value.
       */
    this.selected = this.value
    this.dateString = this.value
  }
}
</script>
