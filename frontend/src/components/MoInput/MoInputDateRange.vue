<template>
  <div class="form-row">
    <span class="btn btn-link" v-if="hidden">
      <a @click="hidden=false">
        {{$t('buttons.select_another_date')}}
      </a>
    </span>

    <mo-input-date
      class="from-date col"
      :label="$t('input_fields.start_date')"
      v-model="validFrom"
      v-if="!hidden"
      :valid-dates="validStartDateRange"
      @input="updateDate()"
      required
    />

    <mo-input-date
      class="to-date col"
      :label="$t('input_fields.end_date')"
      v-model="validTo"
      v-if="!hidden"
      :valid-dates="validEndDateRange"
      :disabled="disableToDate"
      @input="updateDate()"
    />

    <div class="col-1" v-if="!hidden && initiallyHidden">
      <button class="btn btn-sm btn-outline-danger" @click="hidden=true">
        <icon name="minus"/>
      </button>
    </div>
  </div>
</template>

<script>
/**
 * A date picker range component.
 */

import MoInputDate from './MoInputDate'

export default {
  name: 'MoInputDateRange',
  components: {
    MoInputDate
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * This boolean property hides the date.
     */
    initiallyHidden: Boolean,

    /**
     * This boolean property disable the to date.
     */
    disableToDate: Boolean,

    /**
     * Defines disable dates.
     */
    disabledDates: Object
  },

  data () {
    return {
      /**
       * The validFrom, validTo, hidden component value.
       * Used to detect changes and restore the value.
       */
      validFrom: null,
      validTo: null,
      hidden: false
    }
  },

  computed: {
    /**
     * Disable the dates before the choosen start date.
     */
    validStartDateRange () {
      let range = this.getRanges(this.disabledDates)
      if (this.validTo && (!range.to || new Date(this.validTo) < range.to)) {
        range.to = new Date(this.validTo)
      }
      return range
    },

    /**
     * Disable the dates after the choosen end date.
     */
    validEndDateRange () {
      let range = this.getRanges(this.disabledDates)
      if (this.validFrom && new Date(this.validFrom) > range.from) {
        range.from = new Date(this.validFrom)
      }
      return range
    }
  },

  watch: {
    /**
     * Whenever value change, update the from and to date.
     */
    value: {
      handler (newVal) {
        if (this.hidden) {
          this.validFrom = newVal.from
          this.validTo = newVal.to
        }
      },
      deep: true
    }
  },

  created () {
    /**
     * Called synchronously after the instance is created.
     * Set the from and to date to value.
     */
    this.hidden = this.initiallyHidden
    if (this.value !== undefined) {
      this.validFrom = this.value.from
      this.validTo = this.value.to
    }
  },

  methods: {
    /**
     * Valid from and to dates in the date picker for orgUnitValidity and disabledDates.
     */
    getRanges (disabledDates) {
      let range = {
        from: null,
        to: null
      }
      let toFrom = [
        disabledDates['orgUnitValidity'] && disabledDates['orgUnitValidity'].to ? new Date(disabledDates['orgUnitValidity'].to) : null,
        disabledDates['orgUnitValidity'] && disabledDates['orgUnitValidity'].from ? new Date(disabledDates['orgUnitValidity'].from) : null,
        disabledDates['disabledDates'] && disabledDates['disabledDates'].to ? new Date(disabledDates['disabledDates'].to) : null,
        disabledDates['disabledDates'] && disabledDates['disabledDates'].from ? new Date(disabledDates['disabledDates'].from) : null
      ]
      if (toFrom[0] > toFrom[2]) {
        range.to = toFrom[2]
      } else {
        range.to = toFrom[0]
      }
      if (toFrom[1] > toFrom[3]) {
        range.from = toFrom[1]
      } else {
        range.from = toFrom[3]
      }
      return range
    },

    /**
     * Update the from and to date.
     */
    updateDate () {
      let obj = {
        from: null,
        to: null
      }
      if (this.validFrom) {
        obj.from = this.validFrom
      }
      if (this.validTo) {
        obj.to = this.validTo
      }
      this.$emit('input', obj)
    }
  }
}
</script>
