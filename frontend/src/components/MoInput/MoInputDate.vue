SPDX-FileCopyrightText: 2019-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="form-group">
    <label v-if="hasLabel" :for="identifier">{{ label }}</label>

    <date-time-picker
      :open-date="initialValue"
      :language="currentLanguage"
      :clear-button="clearButton"
      :disabled-dates="disabledDates"
      :disabled="disabled"
      v-model="internalValue"
      format="dd-MM-yyyy"
      monday-first
      bootstrap-styling
    />

    <input
      :name="identifier"
      :data-vv-as="label"
      v-model="internalValue"
      type="hidden"
      :v-validate="{ required: required, date_in_range: validDates }"
    />

    <span v-if="errors" v-show="errors.has(identifier)" class="text-danger">
      {{ errors.first(identifier) }}
    </span>
  </div>
</template>

<script>
/**
 * A date picker component.
 */

import DateTimePicker from "vuejs-datepicker"
import moment from "moment"
import MoInputBase from "./MoInputBase"
import { getDatepickerLocales } from "@/i18n.js"

export default {
  extends: MoInputBase,
  name: "MoInputDate",
  components: {
    DateTimePicker,
  },

  props: {
    /**
     * Set valid date interval
     * @default null
     * @type {Object}
     */
    validDates: Object,

    /**
     * Whether to display 'clear' button
     * @default true
     * @type {Boolean}
     */
    clearButton: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return getDatepickerLocales()
  },

  computed: {
    /**
     * The initially focused value. Use either the current value or the
     * closest allowed value.
     */
    initialValue() {
      let currentDate = this.internalValue ? new Date(this.internalValue) : new Date()
      let disabled = this.disabledDates

      if (disabled.to && currentDate <= disabled.to) return disabled.to
      else if (disabled.from && currentDate < disabled.from) return disabled.from
      else return currentDate
    },

    /**
     * Date interval to disable.
     * We flip the validTo dates, as we want to disable anything outside of the range.
     * @type {Object}
     */
    disabledDates() {
      return {
        from:
          this.validDates && this.validDates.to ? new Date(this.validDates.to) : null,
        to:
          this.validDates && this.validDates.from
            ? new Date(this.validDates.from)
            : null,
      }
    },

    currentLanguage() {
      return getDatepickerLocales()[this.$i18n.locale]
    },
  },

  watch: {
    /**
     * Send on a date-only string in ISO format, so that we
     * disregard timezones and the time-of-day.
     */
    internalValue(newVal) {
      let modifiedValue = newVal
        ? moment.utc(new Date(newVal)).format("YYYY-MM-DD")
        : null
      this.$emit("input", modifiedValue)
    },
  },
}
</script>
