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
        :name="nameId"
        :data-vv-as="label" 
        v-model="selected"
        type="hidden"
        v-validate="{required: required}">

      <span v-show="errors.has(nameId)" class="text-danger">{{ errors.first(nameId) }}</span>
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
  computed: {
    nameId () {
      return 'date-picker-' + this._uid
    }
  },
  watch: {
    selected (newVal) {
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
