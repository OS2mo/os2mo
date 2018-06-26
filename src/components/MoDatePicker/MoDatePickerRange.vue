<template>
  <div class="form-row">
    <span v-show="hidden">
      <button class="btn btn-link" @click="hidden=false">
        {{$t('buttons.select_another_date')}}
      </button>
    </div>
    <mo-date-picker 
      class="from-date"
      :label="$t('input_fields.start_date')"
      v-model="validFrom"
      v-show="!hidden"
      :valid-dates="validStartDateRange"
      @input="updateDate()"
      required
    />

    <mo-date-picker 
      class="to-date"
      :label="$t('input_fields.end_date')"
      v-model="validTo"
      v-show="!hidden"
      :valid-dates="validEndDateRange"
      :disabled="disableToDate"
      @input="updateDate()"
    />
  </div>
</template>

<script>
  import MoDatePicker from '@/components/atoms/MoDatePicker'

  export default {
    components: {
      MoDatePicker
    },
    props: {
      value: Object,
      initiallyHidden: Boolean,
      disableToDate: Boolean,
      disabledDates: Object
    },
    data () {
      return {
        validFrom: null,
        validTo: null,
        hidden: false
      }
    },
    computed: {
      validStartDateRange () {
        let range = {
          from: this.disabledDates && this.disabledDates.from ? new Date(this.disabledDates.from) : null,
          to: this.disabledDates && this.disabledDates.to ? new Date(this.disabledDates.to) : null
        }

        if (this.validTo && (!range.to || Date(this.validTo) < range.to)) {
          range.to = new Date(this.validTo)
        }

        return range
      },

      validEndDateRange () {
        let range = {
          from: this.disabledDates && this.disabledDates.from ? new Date(this.disabledDates.from) : null,
          to: this.disabledDates && this.disabledDates.to ? new Date(this.disabledDates.to) : null
        }

        if (this.validFrom && new Date(this.validFrom) > range.from) {
          range.from = new Date(this.validFrom)
        }

        return range
      }
    },
    watch: {
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
      this.hidden = this.initiallyHidden
      if (this.value !== undefined) {
        this.validFrom = this.value.from
        this.validTo = this.value.to
      }
    },
    methods: {
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
