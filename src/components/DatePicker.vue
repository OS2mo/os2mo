<template>
    <div class="form-group col">
      <label v-if="!noLabel" id="date-label" for="date">{{label}}</label>
      <date-time-picker 
        name="date"
        :data-vv-as="label"
        v-model="selected" 
        format="dd-MM-yyyy"
        language="da" 
        monday-first
        bootstrapStyling
        clear-button
        :disabled="disabled"
       
        v-validate="{ 
          date_format: 'dd-MM-yyyy', 
          required: required 
        }"
      />

      <span
        v-show="errors.has('date')" 
        class="text-danger"
      >
        {{ errors.first('date') }}
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
    value: Date,
    required: Boolean,
    noLabel: Boolean,
    label: {
      default: 'Dato',
      type: String
    },
    disabledTo: Date,
    disabledFrom: Date
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
      this.$emit('input', newVal)
    },

    disabledTo (newVal) {
      this.disabled.to = new Date(newVal)
    },

    disabledFrom (newVal) {
      this.disabled.from = new Date(newVal)
    }
  },
  created () {
    this.selected = this.value
  }
}
</script>
