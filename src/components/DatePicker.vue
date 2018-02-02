<template>
    <div class="form-group col">
      <label 
        v-if="!noLabel"
        id="date-label" 
        for="date"
        >{{label}}</label>
      <date-time-picker 
        name="date"
        :data-vv-as="label"
        v-model="selectedDate" 
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
    label: {
      default: 'Dato',
      type: String
    },
    disabledTo: {
      default: null,
      type: Date
    },
    preselectedDate: Date,
    noLabel: Boolean
  },
  data () {
    return {
      selectedDate: null,
      disabled: {
        to: null,
        from: null
      }
    }
  },
  watch: {
    selectedDate (newVal, oldVal) {
      this.$emit('input', newVal)
    },
    disabledTo (newVal, oldVal) {
      this.disabled.to = newVal
    }
  },
  created () {
    this.selectedDate = this.preselectedDate
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>