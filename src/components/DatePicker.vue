<template>
    <div class="form-group col">
      <label v-if="!noLabel" id="date-label" for="date">{{label}}</label>
      <date-time-picker 
        v-model="selected" 
        format="dd-MM-yyyy"
        language="da" 
        monday-first
        bootstrapStyling
        clear-button
        :disabled="disabled"
      />

      <input 
        :name="id"
        :data-vv-as="label" 
        v-model="selected"
        type="hidden"
        v-validate="{ date_format: 'YYYY-MM-DD', required: required }">

      <span
        v-show="errors.has(id)" 
        class="text-danger"
      >
        {{ errors.first(id) }}
      </span>
    </div>
</template>

<script>

import DateTimePicker from 'vuejs-datepicker'

export default {
  components: {
    DateTimePicker
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: [Date, String],
    id: {type: String, default: 'date-picker'},
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
      let date = newVal
      if (newVal != null) {
        date = new Date(newVal).toISOString().split('T')[0]
      }
      this.$emit('input', date)
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
